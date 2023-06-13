from __future__ import annotations
import os
from copy import copy
import struct
from inspect import isclass
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
    subpackages,
    classproperty,
    fspaths_converter,
    to_mime_format_name,
    from_mime_format_name,
    STANDARD_NAMESPACES,
    add_exc_note,
    describe_task,
    CifsMountIndentifier,
)
from .converter import SubtypeVar
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

FILE_CHUNK_LEN_DEFAULT = 8192


logger = logging.getLogger("fileformats")


class DataType:
    is_fileset = False
    is_field = False

    @classmethod
    def type_var(cls, name):
        return SubtypeVar(name, cls)

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

    @classmethod
    def issubtype(cls, super_type: type, allow_same: bool = True):
        """Check to see whether datatype class is a subtype of a given super class.
        In this case the subtype is expected to be able to be treated as if it was
        the super class.

        Overridden in the ``WithClassifiers`` mixin to add support for
        classified subtypes

        Parameters
        ----------
        super_type : type
            the class to check whether the given class is a subtype of
        allow_same : bool, optional
            whether there is a match if the classes are the same, by default True

        Returns
        -------
        is_subtype : bool
            whether or not the current class can be considered a subtype of the super (or
            is the super itself)
        """
        if allow_same and cls is super_type:
            return True
        if isinstance(super_type, SubtypeVar):
            super_type = super_type.base
        return issubclass(cls, super_type)

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

    @classmethod
    def get_converter(cls, source_format: type, name: str = "converter", **kwargs):
        if source_format.issubtype(cls):
            return None
        else:
            raise FormatConversionError(
                f"Cannot converter between '{cls.mime_like}' and '{source_format.mime_like}'"
            )

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
        mime = f"{cls.namespace}/{to_mime_format_name(cls.__name__)}"
        try:
            cls.from_mime(mime)
        except FormatRecognitionError as e:
            add_exc_note(
                e,
                (
                    f"Cannot create reversible MIME type for {cls} as it is not present "
                    f"in a top-level fileformats namespace package '{cls.namespace}'"
                ),
            )
            raise e
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
        try:
            namespace, format_name = mime_string.split("/")
        except ValueError:
            raise FormatRecognitionError(
                f"Format '{mime_string}' is not a valid MIME-like format of <namespace>/<format>"
            )
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
                if "+" in format_name:
                    qualifier_names, classified_name = format_name.split("+")
                    try:
                        classifiers = [
                            getattr(module, from_mime_format_name(q))
                            for q in qualifier_names.split(".")
                        ]
                    except AttributeError:
                        raise FormatRecognitionError(
                            f"Could not load classifiers [{qualifier_names}] from "
                            f"fileformats.{namespace}, corresponding to MIME, "
                            f"or MIME-like, type {mime_string}"
                        ) from None
                    try:
                        classified = getattr(
                            module, from_mime_format_name(classified_name)
                        )
                    except AttributeError:
                        try:
                            classified = cls.generically_qualifies_by_name[
                                classified_name
                            ]
                        except KeyError:
                            raise FormatRecognitionError(
                                f"Could not load classified class '{classified_name}' from "
                                f"fileformats.{namespace} or list of generic types "
                                f"({list(cls.generically_qualifies_by_name)}), "
                                f"corresponding to MIME, or MIME-like, type {mime_string}"
                            ) from None
                    klass = classified[classifiers]
                else:
                    raise FormatRecognitionError(
                        f"Did not find '{class_name}' class in fileformats.{namespace} "
                        f"corresponding to MIME, or MIME-like, type {mime_string}"
                    ) from None
        return klass

    @classproperty
    def generically_qualifies_by_name(cls):
        if cls._generically_qualifies_by_name is None:
            cls._generically_qualifies_by_name = {
                to_mime_format_name(f.__name__): f
                for f in FileSet.all_formats
                if getattr(f, "generically_qualifies", False)
            }
        return cls._generically_qualifies_by_name

    _generically_qualifies_by_name = None  # Register all generically classified types


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
        link_type: ty.Optional[str] = None,
        trim: bool = True,
        make_dirs: bool = False,
        overwrite: bool = False,
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
        link_type : str, optional
            Whether to use hard ('hard') or symbolic ('symbolic') links instead of
            copying files to the new location. If None then the files are copied,
            None by default.
        trim : bool, optional
            Only copy the paths in the file-set that are "required" by the format,
            true by default
        make_dirs : bool, optional
            Make the parent destination and all missing ancestors if they are missing,
            false by default
        overwrite : bool, optional
            whether to overwrite existing files/directories if present
        """
        dest_dir = Path(dest_dir)  # ensure a Path not a string
        if make_dirs:
            dest_dir.mkdir(parents=True, exist_ok=True)
        if link_type is None:
            copy_dir = shutil.copytree
            copy_file = shutil.copyfile
        elif link_type == "hard":
            copy_file = os.link

            def hardlink_dir(src: Path, dest: Path):
                for dpath, _, fpaths in os.walk(src):
                    dpath = Path(dpath)
                    relpath = dpath.relative_to(src)
                    (dest / relpath).mkdir()
                    for fpath in fpaths:
                        os.link(dpath / fpath, dest / relpath / fpath)

            copy_dir = hardlink_dir
        elif link_type == "symbolic":
            copy_dir = copy_file = os.symlink
        elif link_type == "symbolic_with_cifs_fallback":

            def symlink_dir_w_fallback(src: Path, dest: Path):
                if CifsMountIndentifier.on_cifs(src):
                    shutil.copytree(src, dest)
                else:
                    os.symlink(src, dest)

            def symlink_file_w_fallback(src: Path, dest: Path):
                if CifsMountIndentifier.on_cifs(src):
                    shutil.copyfile(src, dest)
                else:
                    os.symlink(src, dest)

            copy_dir = symlink_dir_w_fallback
            copy_file = symlink_file_w_fallback
        else:
            raise FileFormatsError(
                f"Unrecognised link_type option {link_type}, can be 'hard', 'symbolic' "
                "'symbolic_with_cifs_fallback', or None"
            )
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


@attrs.define
class Field(DataType):
    value = attrs.field()

    type = None
    is_field = True
    primitive = None

    def __str__(self):
        return str(self.value)

    @property
    def metadata(self):
        return {}

    @classproperty
    def all_fields(cls) -> list[ty.Type[Field]]:  # pylint: disable=no-self-argument
        """Iterate over all field formats in fileformats.* namespaces"""
        import fileformats.field  # noqa

        return [f for f in Field.subclasses() if f.primitive is not None]

    @classmethod
    def from_primitive(cls, dtype: type):
        try:
            datatype = next(iter(f for f in cls.all_fields if f.primitive is dtype))
        except StopIteration as e:
            field_types_str = ", ".join(t.__name__ for t in cls.all_fields)
            raise FileFormatsError(
                f"{dtype} doesn't not correspond to a valid fileformats field type "
                f"({field_types_str})"
            ) from e
        return datatype

    _all_fields = None
