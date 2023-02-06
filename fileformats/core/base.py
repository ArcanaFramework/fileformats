import os
from copy import copy
from inspect import isclass
import typing as ty
import importlib
import shutil
from operator import itemgetter
import itertools
from pathlib import Path
import hashlib
import logging
import attrs
from .utils import (
    subpackages,
    classproperty,
    fspaths_converter,
    to_mime_format_name,
    from_mime_format_name,
    STANDARD_NAMESPACES,
    hash_file,
    hash_dir,
)
from .exceptions import (
    FileFormatsError,
    FormatMismatchError,
    FormatConversionError,
    FormatRecognitionError,
)


# Tools imported from Arcana, will remove again once file-formats and "cells"
# have been split
REQUIRED_ANNOTATION = "__fileformats_required__"
CHECK_ANNOTATION = "__fileformats_check__"


logger = logging.getLogger("fileformats")


class DataType:

    is_fileset = False
    is_field = False

    @classmethod
    def matches(cls, values) -> bool:
        """Checks whether the given value (fspaths for file-sets) match the datatype
        specified by the class

        Parameters
        ----------
        values : ty.Any
            values to check whether they match the given datatype

        Returns
        -------
        matches : bool
            whether the datatype matches the provided values
        """
        try:
            cls(values)
        except FormatMismatchError:
            return False
        else:
            return True

    @classproperty
    def namespace(cls):
        """The "namespace" the format belongs to under the "fileformats" umbrella
        namespace"""
        module_parts = cls.__module__.split(".")
        if module_parts[0] != "fileformats":
            raise FileFormatsError(
                f"Cannot create reversible MIME type for {cls} as it is not in the "
                "fileformats namespace"
            )
        return module_parts[1]

    @classproperty
    def all_types(self):
        return itertools.chain(FileSet.all_formats, Field.all_fields)

    @classmethod
    def subclasses(cls):
        """Iterate over all installed subclasses"""
        for subpkg in subpackages():
            for attr_name in dir(subpkg):
                attr = getattr(subpkg, attr_name)
                if isclass(attr) and issubclass(attr, cls):
                    yield attr

    @classproperty
    def mime_like(cls):
        """Generates a "MIME-like" identifier from a format class (i.e.
        an identifier for a non-MIME class in the MIME style), e.g.

            fileformats.text.Plain to "text/plain"

        and

            fileformats.image.TiffFx to "image/tiff-fx"

        Parameters
        ----------
        klass : type(FileSet)
            FileSet subclass
        iana_mime : bool
            whether to use standardised IANA format or a more relaxed type format corresponding
            to the fileformats extension the type belongs to

        Returns
        -------
        type
            the corresponding file format class
        """
        format_name = to_mime_format_name(cls.__name__)
        namespace_module = importlib.import_module("fileformats." + cls.namespace)
        if getattr(namespace_module, cls.__name__, None) is not cls:
            raise FileFormatsError(
                f"Cannot create reversible MIME type for {cls} as it is not present in a "
                f"top-level fileformats namespace package '{cls.namespace}'"
            )
        mime = f"{cls.namespace}/{format_name}"
        return mime

    @classmethod
    def from_mime(cls, mime_string):
        """Resolves a FileFormat class from a MIME (IANA) or "MIME-like" identifier (i.e.
        an identifier for a non-MIME class in the MIME style), e.g.

            "text/plain" resolves to fileformats.text.Plain

        and

            "image/tiff-fx" resolves to fileformats.image.TiffFx

        Parameters
        ----------
        mime_string : str
            MIME identifier

        Returns
        -------
        type
            the corresponding file format class
        """
        namespace, format_name = mime_string.split("/")
        try:
            return FileSet.formats_by_iana_mime[mime_string]
        except KeyError:
            pass
        if namespace == "application":
            # We treat the "application" namespace as a catch-all for any formats that are
            # not explicitly covered by the IANA standard (which is kind of how the IANA
            # treats it). Therefore, we loop through all subclasses across the different
            # namespaces to find one that matches the name.
            if not format_name.startswith("x-"):
                raise FormatRecognitionError(
                    "Did not find class matching official (i.e. non-extension) MIME type "
                    f"{mime_string} (i.e. one not starting with 'application/x-'"
                ) from None
            format_name = format_name[2:]  # remove "x-" prefix
            matching_name = FileSet.formats_by_name[format_name]
            if not matching_name:
                namespace_names = [n.__name__ for n in subpackages()]
                class_name = from_mime_format_name(format_name)
                raise FormatRecognitionError(
                    f"Did not find class matching extension the class name '{class_name}' "
                    f"corresponding to MIME type '{mime_string}' "
                    f"in any of the installed namespaces: {namespace_names}"
                )
            elif len(matching_name) > 1:
                namespace_names = [f.__module__.__name__ for f in matching_name]
                raise FormatRecognitionError(
                    f"Ambiguous extended MIME type '{mime_string}', could refer to "
                    f"{', '.join(repr(f) for f in matching_name)} installed types. "
                    f"Explicitly set the 'iana_mime' attribute on one or all of these types "
                    f"to disambiguate, or uninstall all but one of the following "
                    "namespaces: "
                )
            else:
                klass = next(iter(matching_name))
        else:
            class_name = from_mime_format_name(format_name)
            try:
                module = importlib.import_module("fileformats." + namespace)
            except ImportError:
                raise FormatRecognitionError(
                    f"Did not find fileformats namespace package corresponding to {namespace} "
                    f"required to interpret '{mime_string}' MIME, or MIME-like, type. "
                    f"try installing the namespace package with "
                    f"'python3 -m pip install fileformats-{namespace}'."
                ) from None
            try:
                klass = getattr(module, class_name)
            except AttributeError:
                raise FormatRecognitionError(
                    f"Did not find '{class_name}' class in fileformats.{namespace} "
                    f"corresponding to MIME, or MIME-like, type {mime_string}"
                ) from None
        return klass


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
        default=None, init=False, repr=False, eq=False
    )

    # Explicitly set the Internet Assigned Numbers Authority (https://iana_mime.org) MIME
    # type to None for any base classes that should not correspond to a MIME type.
    iana_mime = None

    # Store converters registered by @converter decorator that convert to FileSet
    # NB: each class will have its own version of this dictionary
    converters = {}

    is_fileset = True

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
            all_str = "\n".join(str(p) for p in fspaths)
            msg = (
                f"The following file system paths provided to {self} do not "
                f"exist:\n{missing_str}\n\nFrom full list:\n{all_str}"
            )
            present_parents = set()
            for fspath in missing:
                if fspath:
                    if fspath.parent.exists():
                        present_parents.add(fspath.parent)
            for parent in present_parents:
                msg += f"\n\nFiles in the present parent directory '{str(fspath.parent)}' are:\n"
                msg += "\n".join(str(p) for p in fspath.parent.iterdir())
            raise FileNotFoundError(msg)

    def __iter__(self):
        return iter(self.fspaths)

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
            try:
                prop = Path(getattr(self, prop_name))
            except TypeError:
                continue
            if prop in self.fspaths:
                required.add(prop)
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

    def copy_to(
        self,
        dest_dir: Path,
        stem: str = None,
        symlink: bool = False,
        trim: bool = True,
        make_dirs: bool = False,
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
        symlink : bool, optional
            Use symbolic links instead of copying files to new location, false by default
        trim : bool, optional
            Only copy the paths in the file-set that are "required" by the format, true by default
        make_dirs : bool, optional
            Make the parent destination and all missing ancestors if they are missing, false by default
        """
        dest_dir = Path(dest_dir)  # ensure a Path not a string
        if make_dirs:
            dest_dir.mkdir(parents=True, exist_ok=True)
        if symlink:
            copy_dir = copy_file = os.symlink
        else:
            copy_dir = shutil.copytree
            copy_file = shutil.copyfile
        new_paths = []
        if trim:
            fspaths_to_copy = self.required_paths()
        else:
            fspaths_to_copy = self.fspaths
        for fspath in fspaths_to_copy:
            new_fname = stem + ".".join(fspath.suffixes) if stem else fspath.name
            new_path = dest_dir / new_fname
            if fspath.is_dir():
                copy_dir(fspath, new_path)
            else:
                copy_file(fspath, new_path)
            new_paths.append(new_path)
        return type(self)(new_paths)

    def select_by_ext(self, fileformat: type = None, allow_none: bool = False) -> Path:
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
    def get_converter(cls, source_format: type, name: str, **kwargs):
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
        if source_format is cls or issubclass(source_format, cls):
            return None
        converter_tuple = None
        # Only access converters to the specific class, not superclasses (which may not
        # be able to convert to the specific type)
        try:
            converters = cls.__dict__["converters"]
        except KeyError:
            raise FormatConversionError(
                f"No converters specified to {cls.mime_like} format (trying to find one from "
                f"{source_format.mime_like}"
            )
        try:
            converter_tuple = converters[source_format]
        except KeyError:  # check to see whether there are converters from a base class
            available = []
            for frmt, converter in converters.items():
                if issubclass(source_format, frmt):
                    available.append(converter)
            if len(available) > 1:
                available_str = "\n".join(str(a) for a in available)
                raise FormatConversionError(
                    f"Ambiguous converters found between '{cls.mime_like}' and "
                    f"'{source_format.mime_like}':\n{available_str}"
                ) from None
            elif not available:
                raise FormatConversionError(
                    f"Could not find converter between '{source_format.mime_like}' and "
                    f"'{cls.mime_like}' formats"
                ) from None
            else:
                converter_tuple = available[0]
        converter, conv_kwargs = converter_tuple
        if kwargs:
            conv_kwargs = copy(conv_kwargs)
            conv_kwargs.update(kwargs)
        return converter(name=name, **conv_kwargs)

    @classproperty
    def all_formats(cls):
        """Iterate over all FileSet formats in fileformats.* namespaces"""
        if cls._all_formats is None:
            cls._all_formats = [
                f for f in FileSet.subclasses() if f.__dict__.get("iana_mime", True)
            ]
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

    def hash_files(
        self,
        crypto=None,
        chunk_len=8192,
        relative_to: os.PathLike = None,
        **kwargs,
    ):
        """Calculate hashes for all files within the file set within a dictionary.
        Hashes for files within directories are nested within separate dictionaries
        for each (sub)directory.

        Parameters
        ----------
        crypto : function, optional
            the cryptography method used to hash the files, by default hashlib.sha256
        chunk_len : int, optional
            the chunk length to break up the file and calculate the hash over, by default 8192
        relative_to : Path, optional
            the base path by which to record the file system paths in the dictionary keys
            to, by default None
        **kwargs
            keyword args passed directly through to the ``hash_dir`` function

        Returns
        -------
        file_hashes : dict[str, str]
            hashes for all files in the file-set, addressed by their directory relative
            to the ``relative_to`` path
        """
        if relative_to is None:
            relative_to = Path(os.path.commonpath(self.fspaths))
            if all(p.is_file() and p.parent == relative_to for p in self.fspaths):
                relative_to /= os.path.commonprefix(
                    [p.name for p in self.fspaths]
                ).rstrip(".")
        if crypto is None:
            crypto = hashlib.sha256

        file_hashes = {}
        for key, fspath in sorted(
            ((str(p)[len(str(relative_to)) :], p) for p in self.fspaths),
            key=itemgetter(0),
        ):
            if fspath.is_file():
                file_hashes[key] = hash_file(fspath, chunk_len=chunk_len, crypto=crypto)
            elif fspath.is_dir():
                file_hashes.update(
                    hash_dir(
                        fspath,
                        chunk_len=chunk_len,
                        crypto=crypto,
                        relative_to=relative_to,
                        **kwargs,
                    )
                )
            else:
                raise RuntimeError(f"Cannot hash {self} as {fspath} no longer exists")
        return file_hashes

    def hash(self, crypto=None, *args, **kwargs):
        """Calculate a unique hash for the file-set based on the relative paths and
        contents of its constituent files

        Parameters
        ----------
        crypto : function, optional
            the cryptography method used to hash the files, by default hashlib.sha256
        chunk_len : int, optional
            the chunk length to break up the file and calculate the hash over, by default 8192
        relative_to : Path, optional
            the base path by which to record the file system paths in the dictionary keys
            to, by default None
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
        for path, hash in self.hash_files(crypto=crypto, *args, **kwargs).items():
            crytpo_obj.update(path.encode())
            crytpo_obj.update(hash.encode())
        return crytpo_obj.hexdigest()

    _all_formats = None
    _formats_by_iana_mime = None
    _formats_by_name = None


@attrs.define
class Field(DataType):

    value = attrs.field()

    type = None
    is_field = True

    def __str__(self):
        return str(self.value)

    @property
    def metadata(self):
        return {}

    @classproperty
    def all_fields(cls):
        """Iterate over all field formats in fileformats.* namespaces"""
        if cls._all_fields is None:
            cls._all_fields = [f for f in Field.subclasses() if f.type is not None]
        return cls._all_fields

    _all_fields = None
