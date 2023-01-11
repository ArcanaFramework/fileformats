from __future__ import annotations
import os
import shutil
from pathlib import Path
import operator
import logging
import attrs
from .utils import splitext
from .exceptions import FileFormatsError, FormatMismatchError, FormatConversionError


# Tools imported from Arcana, will remove again once file-formats and "cells"
# have been split
REQUIRED_ANNOTATION = "__fileformats_required__"
CHECK_ANNOTATION = "__fileformats_check__"


# Ops that can be used to quickly check the value of required properties
REQUIRED_CHECK_OPS = {
    "eq": operator.eq,
    "lt": operator.lt,
    "gt": operator.gt,
    "ge": operator.ge,
    "le": operator.le,
    "ne": operator.ne,
    "is_": operator.is_,
    "in_": lambda x, s: x in s,
    "not_in": lambda x, s: x not in s,
    "issubclass": issubclass,
    "isinstance": isinstance,
}

logger = logging.getLogger("fileformats")


def fspaths_converter(fspaths):
    """Ensures fs-paths are a set of pathlib.Path"""
    if isinstance(fspaths, (str, Path, bytes)):
        fspaths = [fspaths]
    return set((Path(p) if isinstance(p, str) else p).absolute() for p in fspaths)


@attrs.define
class Metadata:

    loaded: dict = attrs.field(factory=dict, converter=dict)
    _fileset = attrs.field(default=None, init=False)

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
                if mismatching := [
                    k
                    for k in set(self.loaded) & set(loaded_dict)
                    if self.loaded[k] != loaded_dict[k]
                ]:
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

    # Create slot to hold converters registered by @converter decorator
    converters = None

    def __attrs_post_init__(self):
        self.metadata._fileset = self
        # Check required properties
        for prop in self.required_properties():
            self._check_property(self, prop)

    @fspaths.validator
    def validate_fspaths(self, _, fspaths):
        if missing := [p for p in fspaths if not p or not p.exists()]:
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
        for attr_name in dir(cls):
            klass_attr = getattr(cls, attr_name)
            if isinstance(klass_attr, property):
                try:
                    klass_attr.fget.__annotations__[REQUIRED_ANNOTATION]
                except KeyError:
                    pass
                else:
                    yield attr_name

    @classmethod
    def checks(cls):
        """Find all methods used to check the validity of the file format

        Returns
        -------
        iter(str)
            an iterator over all method names marked as a "check"
        """
        # Loop through all attributes and find methods marked by CHECK_ANNOTATION
        for attr_name in dir(cls):
            klass_attr = getattr(cls, attr_name)
            try:
                klass_attr.__annotations__[CHECK_ANNOTATION]
            except (AttributeError, KeyError):
                pass
            else:
                yield attr_name

    def copy(self, dest_dir: Path, stem: str = None, symlink: bool = False):
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
        """
        dest_dir = Path(dest_dir)  # ensure a Path not a string
        if symlink:
            copy_dir = copy_file = os.symlink
        else:
            copy_dir = shutil.copytree
            copy_file = shutil.copyfile
        new_paths = []
        for fspath in self.fspaths:
            new_fname = stem + ".".join(fspath.suffixes) if stem else fspath.name
            new_path = dest_dir / new_fname
            if fspath.is_dir():
                copy_dir(fspath, new_path)
            else:
                copy_file(fspath, new_path)
            new_paths.append(new_path)
        return type(self)(new_paths)

    def select_by_ext(self, ext: str) -> Path:
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
        matches = self.matching_ext(self.fspaths, ext)
        if not matches:
            paths_str = ", ".join(str(p) for p in self.fspaths)
            raise FormatMismatchError(
                f"No matching files with '{ext}' extension found in "
                f"file set {paths_str}"
            )
        elif len(matches) > 1:
            matches_str = ", ".join(str(p) for p in matches)
            raise FormatMismatchError(
                f"Multiple files with '{ext}' extension found in : {matches_str}"
            )
        return matches[0]

    @classmethod
    def matching_ext(cls, fspaths: set[Path], ext: str) -> list[Path]:
        """Returns the paths out of the candidates provided that matches the
        given extension (by default the extension of the class)

        Parameters
        ----------
        fspaths: list[Path]
            The paths to select from
        ext: str or None
            the extension to match (defaults to 'ext' attribute of class)

        Returns
        -------
        list[Path]
            the matching paths

        Raises
        ------
        FileFormatError
            When no paths match or more than one path matches the given extension"""
        return [p for p in fspaths if str(p).endswith(ext)]

    @classmethod
    def convert(cls, fileset, **kwargs):
        """Convert a given file-set into the format specified by the class

        Parameters
        ----------
        fileset : FileSet
            the file-set object to convert
        **kwargs
            args to pass to the conversion process

        Returns
        -------
        FileSet
            the file-set converted into the type of the current class
        """
        task_spec = cls.find_converter(source_format=type(fileset))
        # Make unique, yet somewhat recognisable task name
        task_name = f"{type(fileset).__name__}_to_{cls.__name__}_{id(fileset)}"
        task = task_spec(name=task_name, in_file=fileset, **kwargs)
        result = task(plugin="serial")
        return cls(result.output.out_file)

    @classmethod
    def find_converter(cls, source_format: type) -> type:
        """Finds a converter that converts from the source format type
        into the format specified by the class

        Parameters
        ----------
        source_format : type
            the format to convert from

        Returns
        -------
        pydra.engine.Task
            a pydra task or workflow that performs the conversion

        Raises
        ------
        FileFormatConversionError
            _description_
        FileFormatConversionError
            _description_
        """
        converter = None
        # Walk back through method-resolution order of base classes to try to find a
        # valid converter
        for klass in cls.mro():
            converters = klass.__dict__.get("converters")
            if converters is None:
                continue
            try:
                converter = converters[source_format]
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
                elif available:
                    converter = available[0]
            if converter:
                break
        if not converter:
            raise FormatConversionError(
                f"Could not find converter between {source_format.__name__} and "
                f"{cls.__name__} formats"
            )
        return converter

    @classmethod
    def include_adjacents(
        cls,
        fspaths: set[Path],
        duplicate_ext: bool = False,
        multipart_ext: bool = True,
    ) -> set[Path]:
        """Adds any "adjacent files", i.e. any files with the same stem but different
        extension, if that suffix isn't already present in the existing fspaths

        Parameters
        ----------
        fspaths : list[Path]
            the paths to find the suffies
        duplicate_ext : bool, optional
            whether to include adjacent files if there is already a file with the same
            extension in the file set
        multipart_ext : bool, optional
            whether to treat paths with multiple "." as having one long suffix,
            e.g. "image.nii.gz"
        """
        # Create a copy of the fspaths provided
        fspaths = set(fspaths)

        for fspath in list(fspaths):
            stem = splitext(fspath, multi=multipart_ext)[0]
            for neighbour in fspath.parent.iterdir():
                neigh_stem, neigh_ext = splitext(neighbour, multi=multipart_ext)
                if neigh_stem == stem:
                    if duplicate_ext or neigh_ext not in (
                        splitext(p, multi=multipart_ext)[-1] for p in fspaths
                    ):
                        fspaths.add(neighbour)
        return fspaths

    @classmethod
    def with_adjacents(
        cls,
        fspaths: set[Path],
        **kwargs,
    ):
        """Factory method to create a file-set with adjacent files included

        Parameters
        ----------
        fspaths : list[Path]
            the paths to find the suffies
        duplicate_ext : bool, optional
            whether to include adjacent files if there is already a file with the same
            extension in the file set
        multipart_ext : bool, optional
            whether to treat paths with multiple "." as having one long suffix,
            e.g. "image.nii.gz"
        **kwargs
            keyword arguments passed on to file-set __init__
        """
        fspaths = fspaths_converter(fspaths)
        return cls(cls.include_adjacents(fspaths=fspaths, **kwargs))

    @classmethod
    def _check_property(cls, fileset: FileSet, name: str):
        """Check the value of a property of the file-set to ensure it meets the given
        criteria

        Parameters
        ----------
        fileset : FileSet
            the file-set to check
        name : str
            name of the property to check
        checks : dict[str, ty.Any]
            checks to run against the value of the property

        Raises
        ------
        FileFormatError
            If the value of the property fails to meet any of the checks
        """
        value = getattr(fileset, name)
        failed = []
        if checks := getattr(cls, name).fget.__annotations__[REQUIRED_ANNOTATION]:
            for op, operand in checks.items():
                if not REQUIRED_CHECK_OPS[op](value, operand):
                    failed.append(
                        f"Value of '{name}' property ({value}) is not {op}: {operand}"
                    )
        else:
            assert (
                value is not None
            ), f"'{name}' property of {fileset} should not be None"
        if failed:
            raise FormatMismatchError(
                f"Check of {fileset} failed:\n" + "\n".join(failed)
            )

    # @classmethod
    # def find_converter(cls, from_format):
    #     """Selects the converter method from the given datatype. Will select the
    #     most specific conversion.

    #     Parameters
    #     ----------
    #     from_format : type
    #         The datatype type to convert from

    #     Returns
    #     -------
    #     function or NoneType
    #         The bound method that adds rows to a given workflow if conversion is required
    #         and None if no conversion is required

    #     Raises
    #     ------
    #     FileFormatConversionError
    #         _description_
    #     """
    #     if from_format is cls or issubclass(from_format, cls):
    #         return None  # No conversion is required
    #     converter = None
    #     for attr_name in dir(cls):
    #         meth = getattr(cls, attr_name)
    #         try:
    #             converts_from = meth.__annotations__[CONVERTER_ANNOTATIONS]
    #         except (AttributeError, KeyError):
    #             pass
    #         else:
    #             if from_format is converts_from or issubclass(
    #                 from_format, converts_from
    #             ):
    #                 if converter:
    #                     prev_converts_from = converter.__annotations__[
    #                         CONVERTER_ANNOTATIONS
    #                     ]
    #                     if issubclass(converts_from, prev_converts_from):
    #                         converter = meth
    #                     elif not issubclass(prev_converts_from, converts_from):
    #                         raise FileFormatConversionError(
    #                             f"Ambiguous converters between {from_format} "
    #                             f"and {cls}: {converter} and {meth}. Please "
    #                             f"define a specific converter from {from_format} "
    #                             f"(i.e. instead of from {prev_converts_from} "
    #                             f"and {converts_from} respectively)"
    #                         )
    #                 else:
    #                     converter = meth
    #     if converter is None:
    #         raise FileFormatConversionError(
    #             f"No datatype converters are defined from {from_format} to {cls}"
    #         )
    #     return converter

    # @classmethod
    # def access_contents_task(cls, fileset_lf: LazyField):
    #     """Access the fs paths of the file set"""

    # @classmethod
    # def from_fspath(cls, fspath):
    #     fileset = cls(path=Path(fspath).stem)
    #     fileset.set_fspaths([fspath])
    #     return fileset

    # @classmethod
    # def append_ext(cls, path: Path):
    #     if path.ext is not None:
    #         path = path.with_suffix(cls.ext)
    #     return path

    # @classmethod
    # def converter_task(cls, from_format, name, **kwargs):
    #     """Adds a converter row to a workflow

    #     Parameters
    #     ----------
    #     from_format : type
    #         the file-set class to convert from
    #     taks_name: str
    #         the name for the converter task
    #     **kwargs: dict[str, ty.Any]
    #         keyword arguments passed through to the converter

    #     Returns
    #     -------
    #     Workflow
    #         Pydra workflow to perform the conversion with an input called
    #         'to_convert' and an output called 'converted', which take and
    #         produce file-sets in `from_format` and `cls` types respectively.
    #     """

    #     wf = Workflow(name=name, input_spec=["to_convert"])

    #     # Get row to extract paths from file-set lazy field
    #     wf.add(
    #         func_task(
    #             access_paths,
    #             in_fields=[("from_format", type), ("fileset", from_format)],
    #             out_fields=[(i, Path) for i in from_format.fs_names()],
    #             # name='extract',
    #             from_format=from_format,
    #             fileset=wf.lzin.to_convert,
    #         )
    #     )

    #     # Aggregate converter inputs and combine with fixed keyword args
    #     conv_inputs = {
    #         n: getattr(wf.access_paths.lzout, n) for n in from_format.fs_names()
    #     }
    #     conv_inputs.update(kwargs)
    #     # Create converter node
    #     converter, output_lfs = cls.find_converter(from_format)(**conv_inputs)
    #     # If there is only one output lazy field, place it in a tuple so it can
    #     # be zipped with cls.fs_names()
    #     if isinstance(output_lfs, LazyField):
    #         output_lfs = (output_lfs,)
    #     # converter.name = 'converter'
    #     # for lf in output_lfs:
    #     #     lf.name = 'converter'
    #     wf.add(converter)

    #     # Encapsulate output paths from converter back into a file set object
    #     to_encapsulate = dict(zip(cls.fs_names(), output_lfs))

    #     logger.debug("Paths to encapsulate are:\n%s", to_encapsulate)

    #     wf.add(
    #         func_task(
    #             encapsulate_paths,
    #             in_fields=[("to_format", type), ("to_convert", from_format)]
    #             + [(o, ty.Union[str, Path]) for o in cls.fs_names()],
    #             out_fields=[("converted", cls)],
    #             # name='encapsulate',
    #             to_format=cls,
    #             to_convert=wf.lzin.to_convert,
    #             **to_encapsulate,
    #         )
    #     )

    #     wf.set_output(("converted", wf.encapsulate_paths.lzout.converted))

    #     return wf


# def access_paths(from_format, fileset):
#     """Copies files into the CWD renaming so the basenames match
#     except for extensions"""
#     logger.debug(
#         "Extracting paths from %s (%s format) before conversion",
#         fileset,
#         from_format,
#     )
#     cpy = fileset.copy_to(path2varname(fileset.path), symlink=True)
#     return cpy.fspaths if len(cpy.fspaths) > 1 else cpy.fspath


# def encapsulate_paths(to_format: type, to_convert: FileSet, **fspaths: ty.List[Path]):
#     """Copies files into the CWD renaming so the basenames match
#     except for extensions"""
#     logger.debug("Encapsulating %s into %s format after conversion", fspaths, to_format)
#     fileset = to_format(to_convert.path + "_" + to_format.class_name())
#     fileset.set_fspaths(fspaths.values())
#     return fileset


# @attrs.define
# class Field(DataType):
#     """
#     A representation of a value field in the dataset.

#     Parameters
#     ----------
#     name_path : str
#         The name_path to the relative location of the field, i.e. excluding
#         information about which row in the data tree it belongs to
#     derived : bool
#         Whether or not the value belongs in the derived session or not
#     row : DataRow
#         The data row that the field belongs to
#     exists : bool
#         Whether the field exists or is just a placeholder for a sink
#     provenance : Provenance | None
#         The provenance for the pipeline that generated the field,
#         if applicable
#     """

#     value: ty.Any = None

#     def get(self, assume_exists=False):
#         if not assume_exists:
#             self._check_exists()
#         self._check_part_of_row()
#         self.value = self.row.dataset.store.get_field_value(self)

#     def put(self, value):
#         self._check_part_of_row()
#         self.row.dataset.store.put_field_value(self, self.format(value))
#         self.exists = True

#     def __int__(self):
#         return int(self.value)

#     def __float__(self):
#         return float(self.value)

#     def __str__(self):
#         if self.datatype.__args__:  # Sequence type
#             val = "[" + ",".join(self._to_str(v) for v in self.value) + "]"
#         else:
#             val = self._to_str(self.value)
#         return val

#     def _to_str(self, val):
#         if self.datatype is str:
#             val = '"{}"'.format(val)
#         else:
#             val = str(val)
#         return val

#     def get_checksums(self):
#         """
#         For duck-typing with filesets in checksum management. Instead of a
#         checksum, just the value of the field is used
#         """
#         return self.value
