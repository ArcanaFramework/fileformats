from __future__ import annotations
import os
from copy import copy
import struct
from enum import Enum
from warnings import warn
import traceback
import typing as ty
import importlib
import shutil
from operator import itemgetter
import itertools
import functools
from pathlib import Path
import hashlib
import logging
import attrs
from .utils import (
    classproperty,
    fspaths_converter,
    to_mime_format_name,
    STANDARD_NAMESPACES,
    describe_task,
)
from .converter import SubtypeVar
from .exceptions import (
    FileFormatsError,
    FormatMismatchError,
    FormatConversionError,
)
from .datatype import DataType

# Tools imported from Arcana, will remove again once file-formats and "cells"
# have been split
REQUIRED_ANNOTATION = "__fileformats_required__"
CHECK_ANNOTATION = "__fileformats_check__"

FILE_CHUNK_LEN_DEFAULT = 8192


logger = logging.getLogger("fileformats")


@attrs.define
class FileSet(DataType):
    """
    The base class for all format types within the fileformats package. A generic
    representation of a collection of files related to a single data resource. A
    file-set can be a single file or directory or a collection thereof, such as a
    primary file with a "side-car" header.

    Parameters
    ----------
    fspaths : set[Path]
        a set of file-system paths pointing to all the resources in the file-set
    checks : bool
        whether to run in-depth "checks" to verify the file format
    """

    fspaths: ty.FrozenSet[Path] = attrs.field(default=None, converter=fspaths_converter)
    _metadata: ty.Dict[str, ty.Any] = attrs.field(
        default=None,
        init=False,
        repr=False,
        eq=False,
        hash=False,
    )

    # Explicitly set the Internet Assigned Numbers Authority (https://iana_mime.org) MIME
    # type to None for any base classes that should not correspond to a MIME or MIME-like
    # type.
    iana_mime = None
    ext = ""

    # Store converters registered by @converter decorator that convert to FileSet
    # NB: each class will have its own version of this dictionary
    converters = {}

    is_fileset = True

    class CopyMode(Enum):
        """Designates the desired behaviour of the FileSet.copy() method"""

        dont_copy = 0b0001  # simply leave the files where they are (i.e. don't copy)
        symlink = 0b0010  # symlink the file into the destination directory
        hardlink = 0b0100  # hardlink the file into the destination directory
        copy = (
            0b1000  # duplicate (actually copy) the file into the destination directory
        )

        link = 0b0110  # use either linking method (preferring symbolic)
        link_or_copy = 0b1110  # use either linking method or copy (preferring symbolic, hardlink and then copy)
        symlink_or_copy = 0b1010
        hardlink_or_copy = 0b1100

        # Masks
        all = 0b1111  # use any method (preferring dont_copy)
        no_supported = 0b0000  # none of the requested methods are supported

        # rarely used combinations
        dont_copy_or_symlink = 0b0011
        dont_copy_or_hardlink = 0b0101
        dont_copy_or_link = 0b0111
        dont_copy_or_symlink_or_copy = 0b1011
        dont_copy_or_hardlink_or_copy = 0b1101

        def __xor__(self, other):
            return type(self)(self.value ^ other.value)

        def __and__(self, other):
            return type(self)(self.value & other.value)

        def __or__(self, other):
            return type(self)(self.value | other.value)

        def __sub__(self, other):
            return type(self)((self.value & (self.value ^ other.value)))

        def __bool__(self):
            return bool(self.value)

    def __hash__(self):
        return hash(sorted(self.fspaths))

    def __repr__(self):
        return f"{type(self).__name__}('" + "', '".join(self.fspaths) + "')"

    def __attrs_post_init__(self):
        # Check required properties don't raise errors
        for prop_name in self.required_properties():
            getattr(self, prop_name)
        # Loop through all attributes and find methods marked by CHECK_ANNOTATION
        for check in self.checks():
            getattr(self, check)()

    @fspaths.validator
    def validate_fspaths(self, _, fspaths):
        if not fspaths:
            raise FileFormatsError(f"No file-system paths provided to {self}")
        missing = [p for p in fspaths if not p or not p.exists()]
        if missing:
            missing_str = "\n".join(str(p) for p in missing)
            msg = (
                f"The following file system paths provided to {type(self)} do not "
                f"exist:\n\n{missing_str}\n\n"
            )
            present_parents = set()
            for fspath in missing:
                if fspath:
                    if fspath.parent.exists():
                        present_parents.add(fspath.parent)
            for parent in present_parents:
                msg += (
                    f"\n\nFiles in the present parent directory '{str(parent)}' are:\n"
                )
                msg += "\n".join(str(p) for p in parent.iterdir())
            raise FileNotFoundError(msg)

    @property
    def metadata(self):
        if self._metadata is None and hasattr(self, "load_metadata"):
            self._metadata = self.load_metadata()
        return self._metadata

    @classproperty
    def mime_type(cls):
        """Generates a MIME type (IANA) identifier from a format class. If an official
        IANA MIME type doesn't exist it will create one in the in the MIME style, e.g.

            fileformats.text.Plain to "text/plain"

            fileformats.image.TiffFx to "image/tiff-fx"

            fileformats.mynamespace.MyFormat to "application/x-my-format

        Returns
        -------
        str
            the MIME type corresponding to the class
        """
        if getattr(cls, "iana_mime", None) is not None:
            mime_type = cls.iana_mime
        else:
            format_name = to_mime_format_name(cls.__name__)
            mime_type = f"application/x-{format_name}"
        return mime_type

    @classmethod
    def required_properties(cls):
        """Find all properties required to treat file-set as being in the format specified
        by the class

        Returns
        -------
        iter(str)
            an iterator over all properties names marked as "required"
        """
        fileset_props = dir(FileSet)
        for attr_name in dir(cls):
            if attr_name in fileset_props:
                continue
            klass_attr = getattr(cls, attr_name)
            if isinstance(klass_attr, property):
                try:
                    klass_attr.fget.__annotations__[REQUIRED_ANNOTATION]
                except KeyError:
                    pass
                else:
                    yield attr_name

    def required_paths(self) -> ty.Set[Path]:
        """Returns all fspaths that are required for the format"""
        required = set()
        for prop_name in self.required_properties():
            prop = getattr(self, prop_name)
            paths = []
            if hasattr(prop, "required_paths"):
                paths = prop.required_paths()
            elif isinstance(prop, os.PathLike):
                paths = [Path(prop)]
            elif isinstance(prop, ty.Iterable):
                for p in prop:
                    if isinstance(p, os.PathLike):
                        paths.append(Path(p))
            for path in paths:
                if path in self.fspaths:
                    required.add(path)
        return required

    def trim_paths(self):
        """Trims paths in fspaths to only those that are "required" by the format class
        i.e. returned by a required property"""
        self.fspaths = fspaths_converter(self.required_paths())
        return self

    @classmethod
    def checks(cls):
        """Find all methods used to check the validity of the file format

        Returns
        -------
        iter(str)
            an iterator over all method names marked as a "check"
        """
        # Loop through all attributes and find methods marked by CHECK_ANNOTATION
        fileset_props = dir(FileSet)
        for attr_name in dir(cls):
            if attr_name in fileset_props:
                continue
            klass_attr = getattr(cls, attr_name)
            try:
                klass_attr.__annotations__[CHECK_ANNOTATION]
            except (AttributeError, KeyError):
                pass
            else:
                yield attr_name

    def copy(
        self,
        dest_dir: Path,
        stem: ty.Optional[str] = None,
        mode: ty.Union[CopyMode, str] = CopyMode.copy,
        trim: bool = True,
        make_dirs: bool = False,
        overwrite: bool = False,
        supported_modes: CopyMode = CopyMode.all,
    ):
        """Copies the file-set to a new directory, optionally renaming the files
        to have consistent name-stems.

        Parameters
        ----------
        dest_dir : str
            Path to the parent directory to save the file-set
        stem: str, optional
            the file name excluding file extensions, to give the files/dirs in the parent
            directory, by default the original file name is used
        mode : CopyMode or str, optional
            designates whether to perform an actual copy or whether a link (symbolic or
            hard) is okay, 'duplicate' by default.
        trim : bool, optional
            Only copy the paths in the file-set that are "required" by the format,
            true by default
        make_dirs : bool, optional
            Make the parent destination and all missing ancestors if they are missing,
            false by default
        overwrite : bool, optional
            whether to overwrite existing files/directories if present
        supported_modes : CopyMode, optional
            supported modes for the copy operation. Used to mask out the requested
            copy mode
        """
        mode = self.CopyMode[mode] if isinstance(mode, str) else mode
        selected_mode = mode & supported_modes
        if not selected_mode:
            raise FileFormatsError(
                f"Cannot copy {self} using {mode} mode as it is not supported "
                f"({supported_modes})"
            )
        if selected_mode & self.CopyMode.dont_copy:
            return self
        dest_dir = Path(dest_dir)  # ensure a Path not a string
        if make_dirs:
            dest_dir.mkdir(parents=True, exist_ok=True)
        if selected_mode & self.CopyMode.symlink:
            copy_dir = copy_file = os.symlink
        elif selected_mode & self.CopyMode.hardlink:
            copy_file = os.link

            def hardlink_dir(src: Path, dest: Path):
                for dpath, _, fpaths in os.walk(src):
                    dpath = Path(dpath)
                    relpath = dpath.relative_to(src)
                    (dest / relpath).mkdir()
                    for fpath in fpaths:
                        os.link(dpath / fpath, dest / relpath / fpath)

            copy_dir = hardlink_dir
        else:
            assert selected_mode & self.CopyMode.copy
            copy_dir = shutil.copytree
            copy_file = shutil.copyfile
        new_paths = []
        if trim and self.required_paths():
            fspaths_to_copy = self.required_paths()
        else:
            fspaths_to_copy = self.fspaths
        if not fspaths_to_copy:
            raise FileFormatsError(
                f"Cannot copy {self} because none of the fspaths in the file-set are "
                "required. Set trim=False to copy all file-paths"
            )
        for fspath in fspaths_to_copy:
            if stem:
                new_fname = stem + "".join(fspath.suffixes)
            else:
                new_fname = fspath.name
            new_path = dest_dir / new_fname
            if new_path.exists():
                if overwrite:
                    if fspath.is_dir():
                        shutil.rmtree(new_path)
                    else:
                        os.unlink(new_path)
                else:
                    raise FileFormatsError(
                        f"Destination path '{str(new_path)}' exists, set "
                        "'overwrite' to overwrite it"
                    )
            if fspath.is_dir():
                copy_dir(fspath, new_path)
            else:
                copy_file(fspath, new_path)
            new_paths.append(new_path)
        return type(self)(new_paths)

    def copy_to(self, *args, **kwargs):
        """For b/w compatibility (temporary message)"""
        warn("'FileSet.copy_to()' has been deprecated, please use copy() instead")
        return self.copy(*args, **kwargs)

    def select_by_ext(
        self, fileformat: ty.Optional[type] = None, allow_none: bool = False
    ) -> Path:
        """Selects a single path from a set of file-system paths based on the file
        extension

        Parameters
        ----------
        fileformat : type
            the format class of the path to select
        allow_none : bool
            whether to return None instead of raising an error if the file is not found

        Returns
        -------
        Path or None
            the selected file-system path that matches the extension or None if not found
            and `allow_none` is True

        Raises
        ------
        FileFormatError
            if no paths match the extension and `allow_none` is False
        FileFormatError
            if more than one paths matches the extension
        """
        if fileformat is None:
            fileformat = type(self)
        exts = [fileformat.ext]
        try:
            exts.extend(fileformat.alternate_exts)
        except AttributeError:
            pass
        matches = self.matching_exts(self.fspaths, exts)
        if not matches:
            if allow_none:
                return None
            paths_str = ", ".join(str(p) for p in self.fspaths)
            raise FormatMismatchError(
                f"No matching files with extensions in {exts} in file set {paths_str}"
            )
        elif len(matches) > 1:
            matches_str = ", ".join(str(p) for p in matches)
            raise FormatMismatchError(
                f"Multiple files with {exts} extensions found in : {matches_str}"
            )
        return matches[0]

    @classmethod
    def matching_exts(cls, fspaths: ty.Set[Path], exts: ty.List[str]) -> ty.List[Path]:
        """Returns the paths out of the candidates provided that matches the
        given extension (by default the extension of the class)

        Parameters
        ----------
        fspaths: list[Path]
            The paths to select from
        ext: list[str]
            the extensions to match

        Returns
        -------
        list[Path]
            the matching paths

        Raises
        ------
        FileFormatError
            When no paths match or more than one path matches the given extension"""
        return [p for p in fspaths if any(str(p).endswith(e) for e in exts)]

    @classmethod
    def convert(cls, fileset, plugin="serial", task_name=None, **kwargs):
        """Convert a given file-set into the format specified by the class

        Parameters
        ----------
        fileset : FileSet
            the file-set object to convert
        plugin : str
            the "execution plugin" used to run the conversion task
        task_name : str
            the name given to the converter task
        **kwargs
            args to pass to the conversion process

        Returns
        -------
        FileSet
            the file-set converted into the type of the current class
        """
        if task_name is None:
            task_name = f"{type(fileset).__name__}_to_{cls.__name__}_{id(fileset)}"
        # Make unique, yet somewhat recognisable task name
        task = cls.get_converter(source_format=type(fileset), name=task_name, **kwargs)
        result = task(in_file=fileset, plugin=plugin)
        out_file = result.output.out_file
        if not isinstance(out_file, cls):
            out_file = cls(out_file)
        return out_file

    @classmethod
    def get_converter(cls, source_format: type, name: str = "converter", **kwargs):
        """Get a converter that converts from the source format type
        into the format specified by the class

        Parameters
        ----------
        source_format : type
            the format to convert from
        name : str
            the name given to the converter task
        **kwargs
            passed on to the task init method to customise the conversion

        Returns
        -------
        pydra.engine.TaskBase or None
            a pydra task or workflow that performs the conversion, or None if no
            conversion is required

        Raises
        ------
        FileFormatConversionError
            no converters found between source and dest format
        FileFormatConversionError
            ambiguous (i.e. more than one) converters found between source and dest format
        """
        if source_format.issubtype(cls):
            return None
        converters = (
            cls.get_converters_dict()
        )  # triggers loading of standard converters for target format
        # Ensure standard converters from source format are loaded
        source_format.import_standard_converters()
        try:
            unclassified = source_format.unclassified
        except AttributeError:
            pass
        else:
            unclassified.import_standard_converters()
        try:
            converter_tuple = converters[source_format]
        except KeyError:
            # If no direct mapping check for mapping from source super types and wildcard
            # matches
            available_converters = cls.get_converter_tuples(source_format)
            if len(available_converters) > 1:
                available_str = "\n".join(
                    describe_task(a[0]) for a in available_converters
                )
                raise FormatConversionError(
                    f"Ambiguous converters found between '{cls.mime_like}' and "
                    f"'{source_format.mime_like}':\n{available_str}"
                ) from None
            elif not available_converters:
                raise FormatConversionError(
                    f"Could not find converter between '{source_format.mime_like}' and "
                    f"'{cls.mime_like}' formats"
                ) from None
            converter_tuple = available_converters[0]
            # Store mapping for future reference
            converters[source_format] = converter_tuple
        converter, conv_kwargs = converter_tuple
        if kwargs:
            # Merge kwargs provided to get_conveter with stored kwargs
            conv_kwargs = copy(conv_kwargs)
            conv_kwargs.update(kwargs)
        return converter(name=name, **conv_kwargs)

    @classmethod
    def get_converters_dict(cls, klass=None):
        # Only access converters to the specific class, not superclasses (which may not
        # be able to convert to the specific type)
        if klass is None:
            klass = cls
        try:
            converters_dict = klass.__dict__["converters"]
        except KeyError:
            converters_dict = {}
            klass.converters = converters_dict
            klass.import_standard_converters()
        return converters_dict

    @classmethod
    def import_standard_converters(cls):
        """Attempts to import standard converters for the format class, which are
        located at `fileformats.<namespace>.converters`
        """
        standard_converters_module = f"fileformats.{cls.namespace}.converters"
        try:
            importlib.import_module(standard_converters_module)
        except ImportError as e:
            if str(e) != f"No module named '{standard_converters_module}'":
                if cls.namespace in STANDARD_NAMESPACES:
                    pkg = "fileformats"
                else:
                    pkg = f"fileformats-{cls.namespace}"
                warn(
                    f"Could not import standard converters for '{cls.namespace}' namespace, "
                    f"please install '{pkg}' with the 'extended' install option to "
                    f"use converters for {cls.namespace}, i.e.\n\n"
                    f"    $ python3 -m pip install '{pkg}[extended]':\n\n"
                    f"Import error was:\n{traceback.format_exc()}"
                )

    @classmethod
    def get_converter_tuples(
        cls, source_format: type
    ) -> ty.List[ty.Tuple[ty.Callable, ty.Dict[str, ty.Any]]]:
        """Search the registered converters to find any matches and return list of
        task and associated key-word args to perform the conversion between source and
        target formats

        Parameters
        ----------
        source_format : type(FileSet)
            the source format to convert from

        Returns
        -------
        available : list[tuple[TaskBase, dict[str, Any]]]
            list of available converters between the source and target formats
        """
        converters_dict = cls.get_converters_dict()
        available = []
        for src_frmt, converter in converters_dict.items():
            if len(converter) == 2:  # Ignore converters with wildcards at this point
                if source_format.issubtype(src_frmt):
                    available.append(converter)
        if not available and hasattr(source_format, "unclassified"):
            available = SubtypeVar.get_converter_tuples(
                source_format, target_format=cls
            )
        return available

    @classmethod
    def register_converter(
        cls,
        source_format: type,
        converter_tuple: ty.Tuple[ty.Callable, ty.Dict[str, ty.Any]],
    ):
        """Registers a converter task within a class attribute. Called by the
        @fileformats.mark.converter decorator.

        Parameters
        ----------
        source_format : type
            the source format to register a converter from
        task_spec : ty.Callable
            a callable that resolves to a Pydra task
        converter_kwargs : dict
            additional keyword arguments to be passed to the task spec at initialisation
            time

        Raises
        ------
        FormatConversionError
            if there is already a converter registered between the two types
        """
        converters_dict = cls.get_converters_dict()
        # If no converters are loaded, attempt to load from the standard location
        if source_format in converters_dict:
            prev = cls.converters[source_format][0]
            raise FormatConversionError(
                f"There is already a converter registered between {source_format.__name__} "
                f"and {cls.__name__}: {describe_task(prev)}"
            )
        converters_dict[source_format] = converter_tuple

    @classproperty
    def all_formats(cls) -> set:
        """Iterate over all FileSet formats in fileformats.* namespaces"""
        if cls._all_formats is None:
            cls._all_formats = set(
                f for f in FileSet.subclasses() if f.__dict__.get("iana_mime", True)
            )
        return cls._all_formats

    @classproperty
    def standard_formats(cls):
        """Iterate over all formats in the standard fileformats.* namespaces"""
        return (f for f in cls.all_formats if f.namespace in STANDARD_NAMESPACES)

    @classproperty
    def formats_by_iana_mime(cls):
        """a dictionary containing all formats by their IANA MIME type (if applicable)"""
        if cls._formats_by_iana_mime is None:
            cls._formats_by_iana_mime = {
                f.iana_mime: f
                for f in FileSet.all_formats
                if getattr(f, "iana_mime", None) is not None
            }
        return cls._formats_by_iana_mime

    @classproperty
    def formats_by_name(cls):
        """a dictionary containing lists of formats by their translated class names,
        i.e. their can be more than one format with the same translated name"""
        if cls._formats_by_name is None:
            cls._formats_by_name = {
                k: set(v for _, v in g)
                for k, g in itertools.groupby(
                    sorted(
                        (
                            (to_mime_format_name(f.__name__), f)
                            for f in FileSet.all_formats
                            if getattr(f, "iana_mime", None) is None
                        ),
                        key=itemgetter(0),
                    ),
                    key=itemgetter(0),
                )
            }
        return cls._formats_by_name

    @property
    def all_file_paths(self) -> ty.Iterable[Path]:
        """Paths of all files within the fileset"""
        for fspath in self.fspaths:
            if fspath.is_file():
                yield fspath
            else:
                for dpath, _, file_paths in os.walk(fspath):
                    for file_path in file_paths:
                        yield Path(dpath) / file_path

    def byte_chunks(
        self,
        mtime: bool = False,
        chunk_len=FILE_CHUNK_LEN_DEFAULT,
        relative_to: ty.Optional[os.PathLike] = None,
        ignore_hidden_files: bool = False,
        ignore_hidden_dirs: bool = False,
    ) -> ty.Generator[str, ty.Generator[bytes]]:
        """Yields relative paths for all files within the file-set along with iterators
        over their byte-contents. To be used when generating hashes for the file set.

        Parameters
        ----------
        mtime : bool, optional
            instead of iterating over the entire contents of the file-set, simply yield
            a bytes repr of the last modification time.
        chunk_len : int, optional
            the chunk length to break up the file and calculate the hash over, by default 8192
        relative_to : Path, optional
            the base path by which to record the file system paths in the dictionary keys
            to, by default None
        ignore_hidden_files : bool
            whether to ignore hidden files within nested directories (i.e. those
            starting with '.')
        ignore_hidden_dirs : bool
            whether to ignore hidden directories within nested directories (i.e. those
            starting with '.')

        Yields
        -------
        rel_path: str
            relative path to either 'relative_to' arg or common base path for each file
            in the file set
        byte_iter : Generator[bytes]
            an iterator over the bytes contents of the file, chunked into 'chunk_len'
            chunks
        """
        # If "relative_to" is not provided, get the common path between
        if relative_to is None:
            relative_to = Path(os.path.commonpath(self.fspaths))
            if all(p.is_file() and p.parent == relative_to for p in self.fspaths):
                relative_to /= os.path.commonprefix(
                    [p.name for p in self.fspaths]
                ).rstrip(".")
        # yield the absolute base path if using mtimes instead of contents
        if mtime:
            yield ("<base-path>", iter([str(relative_to.absolute()).encode()]))

        relative_to = str(relative_to)
        if Path(relative_to).is_dir() and not relative_to.endswith(os.path.sep):
            relative_to += os.path.sep

        if mtime:

            def chunk_file(fspath: Path):
                """Yields a byte representation of the last modified time for the file"""
                yield bytes(struct.pack("<d", os.stat(fspath).st_mtime))

        else:

            def chunk_file(fspath: Path):
                """Yields the contents of the file in byte chunks"""
                if not fspath.is_file():
                    assert fspath.is_symlink()  # broken symlink
                    yield b"\x00"
                else:
                    with open(fspath, "rb") as fp:
                        for chunk in iter(functools.partial(fp.read, chunk_len), b""):
                            yield chunk

        def chunk_dir(fspath):
            for dpath, _, filenames in sorted(os.walk(fspath)):
                # Sort in-place to guarantee order.
                filenames.sort()
                dpath = Path(dpath)
                if (
                    ignore_hidden_dirs
                    and dpath.name.startswith(".")
                    and str(dpath) != fspath
                ):
                    continue
                for filename in filenames:
                    if ignore_hidden_files and filename.startswith("."):
                        continue
                    yield (
                        str((dpath / filename).relative_to(relative_to)),
                        chunk_file(dpath / filename),
                    )

        for key, fspath in sorted(
            ((str(p)[len(relative_to) :], p) for p in self.fspaths),
            key=itemgetter(0),
        ):
            if fspath.is_dir():
                yield from chunk_dir(fspath)
            else:
                yield (key, chunk_file(fspath))

    def hash(self, crypto=None, **kwargs) -> bytes:
        """Calculate a unique hash for the file-set based on the relative paths and
        contents of its constituent files

        Parameters
        ----------
        crypto : function, optional
            the cryptography method used to hash the files, by default hashlib.sha256
        **kwargs
            keyword args passed directly through to the ``hash_dir`` function

        Returns
        -------
        hash : str
            unique hash for the file-set
        """
        if crypto is None:
            crypto = hashlib.sha256
        crytpo_obj = crypto()
        for path, bytes_iter in self.byte_chunks(**kwargs):
            crytpo_obj.update(path.encode())
            for bytes_str in bytes_iter:
                crytpo_obj.update(bytes_str)
        return crytpo_obj.hexdigest()

    def hash_files(self, crypto=None, **kwargs) -> dict[str, bytes]:
        """Calculate hashes for all files in the file-set based on the relative paths and
        contents of its constituent files

        Parameters
        ----------
        crypto : function, optional
            the cryptography method used to hash the files, by default hashlib.sha256
        **kwargs
            keyword args passed directly through to the ``hash_dir`` function

        Returns
        -------
        file_hashes : dict[str, bytes]
            unique hashes for each file in the file-set
        """
        if crypto is None:
            crypto = hashlib.sha256
        file_hashes = {}
        for path, bytes_iter in self.byte_chunks(**kwargs):
            crypto_obj = crypto()
            for bytes_str in bytes_iter:
                crypto_obj.update(bytes_str)
            file_hashes[str(path)] = crypto_obj.hexdigest()
        return file_hashes

    def __bytes_repr__(
        self, cache: dict
    ) -> ty.Iterable[bytes]:  # pylint: disable=unused-argument
        """Provided for compatibility with Pydra's hashing function, return the contents
        of all the files in the file-set in chunks

        Parameters
        ----------
        cache : dict
            an object passed around by Pydra's hashing function to store cached versions
            of previously hashed objects, to allow recursive structures

        Yields
        ------
        bytes
            a chunk of bytes of length FILE_CHUNK_LEN_DEFAULT from the contents of all
            files in the file-set.
        """
        cls = type(self)
        yield f"{cls.__module__}.{cls.__name__}:".encode()
        for key, chunk_iter in self.byte_chunks():
            yield (",'" + key + "'=").encode()
            yield from chunk_iter

    _all_formats = None
    _formats_by_iana_mime = None
    _formats_by_name = None
