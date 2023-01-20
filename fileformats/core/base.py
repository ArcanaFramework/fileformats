from __future__ import annotations
import os
from copy import copy
from inspect import isclass
import shutil
from operator import itemgetter
import itertools
from pathlib import Path
import logging
import attrs
from .utils import (
    to_mime,
    subpackages,
    classproperty,
    fspaths_converter,
    to_mime_format_name,
)
from .exceptions import FileFormatsError, FormatMismatchError, FormatConversionError


# Tools imported from Arcana, will remove again once file-formats and "cells"
# have been split
REQUIRED_ANNOTATION = "__fileformats_required__"
CHECK_ANNOTATION = "__fileformats_check__"


logger = logging.getLogger("fileformats")


@attrs.define
class Metadata:

    loaded: dict = attrs.field(factory=dict, converter=dict)
    _fileset = attrs.field(default=None, init=False, repr=False)

    def __iter__(self):
        raise NotImplementedError

    def __getitem__(self, key):
        try:
            return self.loaded[key]
        except KeyError:
            self.load()
        return self.loaded[key]

    def load(self, overwrite=False):
        assert self._fileset is not None
        if hasattr(self._fileset, "load_metadata"):
            loaded_dict = self._fileset.load_metadata()
            if not overwrite:
                mismatching = [
                    k
                    for k in set(self.loaded) & set(loaded_dict)
                    if self.loaded[k] != loaded_dict[k]
                ]
                if mismatching:
                    raise FileFormatsError(
                        "Mismatch in values between loaded and loaded metadata values, "
                        "use 'load(overwrite=True)' to overwrite:\n"
                        + "\n".join(
                            f"{k}: loaded={self.loaded[k]}, loaded={loaded_dict[k]}"
                            for k in mismatching
                        )
                    )
            self.loaded.update(loaded_dict)


@attrs.define
class FileSet:
    """
    The base class for all format types within the fileformats package. A generic
    representation of a collection of files related to a single data resource. A
    file-set can be a single file or directory or a collection thereof, such as a
    primary file with a "side-car" header.

    Parameters
    ----------
    fspaths : set[Path]
        a set of file-system paths pointing to all the resources in the file-set
    metadata : dict[str, Any]
        any metadata that exists outside of the file-set itself. This metadata will be
        augmented by metadata contained within the files if the `load_metadata` method
        is implemented in the file-set subclass
    checks : bool
        whether to run in-depth "checks" to verify the file format
    """

    fspaths: set[Path] = attrs.field(default=None, converter=fspaths_converter)
    metadata: Metadata = attrs.field(factory=dict, converter=Metadata, kw_only=True)

    # Explicitly set the Internet Assigned Numbers Authority (https://iana_mime.org) MIME
    # type to None for any base classes that should not correspond to a MIME type.
    iana_mime = None

    # Store converters registered by @converter decorator that convert to FileSet
    # NB: each class will have its own version of this dictionary
    converters = {}

    def __attrs_post_init__(self):
        self.metadata._fileset = self
        # Check required properties don't raise errors
        for prop_name in self.required_properties():
            getattr(self, prop_name)

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
            for fspath in missing:
                if fspath:
                    if fspath.parent.exists():
                        msg += (
                            f"\n\nFiles in the directory '{str(fspath.parent)}' are:\n"
                        )
                        msg += "\n".join(str(p) for p in fspath.parent.iterdir())
            raise FileNotFoundError(msg)

    def validate(self):
        """Run all checks over the file-set to see whether it matches the specified format

        Raises
        ------
        FormatMismatchError
            if a check fails then a FormatMismatchError will be raised
        """
        # Loop through all attributes and find methods marked by CHECK_ANNOTATION
        for check in self.checks():
            getattr(self, check)()

    def __iter__(self):
        return iter(self.fspaths)

    @classmethod
    def mime(cls):
        """Returns an official MIME type representation of the format, if applicable,
        otherwise a conventional MIME type "extension" of the form "application/x-***"""
        return to_mime(cls, iana_mime=True)

    @classmethod
    def mimelike(cls):
        """Returns a "MIME-like" representation, but with a direct mapping between the
        file-type and the fileformats namespace extension it belongs to"""
        return to_mime(cls, iana_mime=False)

    @classmethod
    def subclasses(cls):
        """Iterate over all installed subclasses"""
        for subpkg in subpackages():
            for attr_name in dir(subpkg):
                attr = getattr(subpkg, attr_name)
                if isclass(attr) and issubclass(attr, cls):
                    yield attr

    @classmethod
    def matches(cls, fspaths: set[Path], validate: bool = True) -> bool:
        """Checks whether the given paths match the format specified by the class

        Parameters
        ----------
        fspaths : set[Path]
            the paths to check whether they match the given format
        checks: bool, optional
            whether to run non-essential checks to determine whether the format matches,
            by default True

        Returns
        -------
        bool
        """
        try:
            fileset = cls(fspaths)
            if validate:
                fileset.validate()
        except FormatMismatchError:
            return False
        else:
            return True

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

    def required_paths(self):
        """Returns all fspaths that are required for the format"""
        required = set()
        for prop_name in self.required_properties:
            prop = getattr(self, prop_name)
            if prop in self.fspaths:
                required.add(prop)

    def trim_paths(self):
        """Trims paths in fspaths to only those that are "required" by the format class
        i.e. returned by a required property"""
        self.fspaths = self.required_paths()

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
        self, dest_dir: Path, stem: str = None, symlink: bool = False, trim: bool = True
    ):
        """Copies the file-set to a new directory, optionally renaming the files
        to have consistent name-stems.

        Parameters
        ----------
        parent : str
            Path to the parent directory to save the file-set
        stem: str, optional
            the file name excluding file extensions, to give the files/dirs in the parent
            directory, by default the original file name is used
        symlink : bool, optional
            Use symbolic links instead of copying files to new location, false by default
        trim : bool, optional
            Only copy the paths in the file-set that are "required" by the format, true by default
        """
        dest_dir = Path(dest_dir)  # ensure a Path not a string
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

    def select_by_ext(self, fileformat: type = None) -> Path:
        """Selects a single path from a set of file-system paths based on the file
        extension

        Parameters
        ----------
        fspaths : set[Path]
            the file-system paths to select from
        ext : str
            the file extension to select

        Returns
        -------
        Path
            the selected file-system path that matches the extension

        Raises
        ------
        FileFormatError
            if no paths match the extension
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
    def matching_exts(cls, fspaths: set[Path], exts: list[str]) -> list[Path]:
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
        task_name : str
            the name given to the converter task
        **kwargs
            passed on to the task init method to customise the conversion

        Returns
        -------
        pydra.engine.TaskBase
            a pydra task or workflow that performs the conversion

        Raises
        ------
        FileFormatConversionError
            _description_
        FileFormatConversionError
            _description_
        """
        converter_tuple = None
        # Only access converters to the specific class, not superclasses (which may not
        # be able to convert to the specific type)
        try:
            converters = cls.__dict__["converters"]
        except KeyError:
            raise FormatConversionError(
                f"No converters specified to {cls} format (trying to find one from "
                f"{source_format}"
            )
        try:
            converter_tuple = converters[source_format]
        except KeyError:  # check to see whether there are converters from a base class
            available = []
            for frmt, converter in converters.items():
                if issubclass(source_format, frmt):
                    available.append(converter)
            if len(available) > 1:
                raise FormatConversionError(
                    f"Ambiguous converters found between {cls.__name__} and "
                    f"{source_format.__name__}, {available}"
                )
            elif not available:
                raise FormatConversionError(
                    f"Could not find converter between {source_format.__name__} and "
                    f"{cls.__name__} formats"
                )
            else:
                converter_tuple = available[0]
        converter, conv_kwargs = converter_tuple
        if kwargs:
            conv_kwargs = copy(conv_kwargs)
            conv_kwargs.update(kwargs)
        # Make recognisable default task name
        # if task_name is None:
        #     task_name = f"{source_format.__name__}_to_{cls.__name__}"
        return converter(name=name, **conv_kwargs)

    @classproperty
    def mimelike_registry(cls):
        module_parts = cls.__module__.split(".")
        if module_parts[0] != "fileformats":
            raise FileFormatsError(
                f"Cannot create reversible MIME type for {cls} as it is not in the "
                "fileformats namespace"
            )
        return module_parts[1]

    @classproperty
    def all_formats(cls):
        if cls._all_formats is None:
            cls._all_formats = [
                f for f in FileSet.subclasses() if f.__dict__.get("iana_mime", True)
            ]
        return cls._all_formats

    @classproperty
    def formats_by_iana_mime(cls):
        if cls._formats_by_iana_mime is None:
            cls._formats_by_iana_mime = {
                f.iana_mime: f
                for f in FileSet.all_formats
                if getattr(f, "iana_mime", None) is not None
            }
        return cls._formats_by_iana_mime

    @classproperty
    def formats_by_name(cls):
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

    _all_formats = None
    _formats_by_iana_mime = None
    _formats_by_name = None
