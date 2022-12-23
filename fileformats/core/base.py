from __future__ import annotations
from pathlib import Path
import typing as ty
from copy import copy
import hashlib
import logging
from abc import ABCMeta, abstractmethod
import attrs
from attrs.converters import optional
from pydra.engine.core import LazyField, Workflow
from .utils import (
    func_task,
    path2varname,
    classproperty,
    CONVERTER_ANNOTATIONS,
    HASH_CHUNK_SIZE,
)
from .exceptions import (
    NameError,
    DataNotDerivedYetError,
    FileFormatError,
    FileFormatConversionError,
    FilePathsNotSetException,
)
from .quality import DataQuality  # @ignore reshadowedImports


def absolute_path(path):
    return Path(path).absolute()


def absolute_paths_dict(dct):
    return {n: absolute_path(p) for n, p in dict(dct).items()}


logger = logging.getLogger("fileformats")


@attrs.define
class DataType(metaclass=ABCMeta):
    """
    A representation of an atomic data item within a dataset. Subclassed to define
    different data file/directory formats and fields

    Parameters
    ----------
    name_path : str
        The name_path to the relative location of the file group, i.e. excluding
        information about which row in the data tree it belongs to
    order : int | None
        The order in which the file-group appears in the row it belongs to
        (starting at 0). Typically corresponds to the acquisition order for
        scans within an imaging session. Can be used to distinguish between
        scans with the same series description (e.g. multiple BOLD or T1w
        scans) in the same imaging sessions.
    quality : str
        The quality label assigned to the file_group (e.g. as is saved on XNAT)
    row : DataRow
        The data row within a dataset that the file-group belongs to
    exists : bool
        Whether the file_group exists or is just a placeholder for a sink
    provenance : Provenance | None
        The provenance for the pipeline that generated the file-group,
        if applicable
    """

    path: str = attrs.field()
    uri: str = attrs.field(default=None)
    order: int = attrs.field(default=None)
    quality: DataQuality = attrs.field(default=DataQuality.usable)
    exists: bool = attrs.field(default=True)
    provenance: ty.Dict[str, ty.Any] = attrs.field(default=None)
    row: ty.Any = attrs.field(default=None)

    SUBPACKAGE = "data"

    @abstractmethod
    def get(self, assume_exists=False):
        """Pulls data from the store (if remote) and caches locally

        Parameters
        ----------
        assume_exists: bool
            If set, checks to see whether the item exists are skipped (used
            to pull data after a successful workflow run)
        """
        raise NotImplementedError

    @abstractmethod
    def put(self, value):
        """Updates the value of the item in the store to the provided value,
        pushing remotely if necessary.

        Parameters
        ----------
        value : ty.Any
            The value to update
        """
        raise NotImplementedError

    @classproperty
    def desc(cls):
        """Descriptive name that can be overridden in subclasses

        Returns
        -------
        _type_
            _description_
        """
        return cls.__name__.lower()

    @property
    def recorded_checksums(self):
        if self.provenance is None:
            return None
        else:
            return self.provenance.outputs[self.name_path]

    @provenance.validator
    def check_provenance(self, _, provenance):
        "Checks that the data item path is present in the provenance"
        if provenance is not None:
            if self.path not in provenance.outputs:
                raise NameError(
                    self.path,
                    f"{self.path} was not found in outputs "
                    f"{provenance.outputs.keys()} of provenance provenance "
                    f"{provenance}",
                )

    def _check_exists(self):
        if not self.exists:
            raise DataNotDerivedYetError(
                self.path, f"Cannot access {self} as it hasn't been derived yet"
            )

    def _check_part_of_row(self):
        if self.row is None:
            raise RuntimeError(f"Cannot 'get' {self} as it is not part of a dataset")

    @classmethod
    def class_name(cls):
        return cls.__name__.lower()


@attrs.define
class FileGroup(DataType, metaclass=ABCMeta):
    """
    A representation of a file_group within the dataset.

    Parameters
    ----------
    name_path : str
        The name_path to the relative location of the file group, i.e. excluding
        information about which row in the data tree it belongs to
    order : int | None
        The order in which the file-group appears in the row it belongs to
        (starting at 0). Typically corresponds to the acquisition order for
        scans within an imaging session. Can be used to distinguish between
        scans with the same series description (e.g. multiple BOLD or T1w
        scans) in the same imaging sessions.
    quality : str
        The quality label assigned to the file_group (e.g. as is saved on XNAT)
    row : DataRow
        The data row within a dataset that the file-group belongs to
    exists : bool
        Whether the file_group exists or is just a placeholder for a sink
    provenance : Provenance | None
        The provenance for the pipeline that generated the file-group,
        if applicable
    fs_path : str | None
        Path to the primary file or directory on the local file system
    side_cars : ty.Dict[str, str] | None
        Additional files in the file_group. Keys should match corresponding
        side_cars dictionary in format.
    checksums : ty.Dict[str, str]
        A checksums of all files within the file_group in a dictionary sorted
        bys relative file name_paths
    """

    ext = None  # to be overridden by file-format specific classes

    fs_path: str = attrs.field(default=None, converter=optional(absolute_path))
    _checksums: ty.Dict[str, str] = attrs.field(default=None, repr=False, init=False)
    # Alternative names for the file format, empty by default overridden in
    # sub-classes where necessary
    alternative_names = ()

    @fs_path.validator
    def validate_fs_path(self, _, fs_path):
        if fs_path is not None:
            if not fs_path.exists:
                raise RuntimeError(
                    "Attempting to set a path that doesn't exist " f"({fs_path})"
                )
            if not self.exists:
                raise RuntimeError(
                    "Attempting to set a path to a file group that hasn't "
                    f"been derived yet ({fs_path})"
                )

    def get(self, assume_exists=False):
        if assume_exists:
            self.exists = True
        self._check_part_of_row()
        fs_paths = self.row.dataset.store.get_file_group_paths(self)
        self.exists = True
        self.set_fs_paths(fs_paths)
        self.validate_file_paths()

    def put(self, *fs_paths):
        self._check_part_of_row()
        fs_paths = [Path(p) for p in fs_paths]
        dir_paths = list(p for p in fs_paths if p.is_dir())
        if len(dir_paths) > 1:
            dir_paths_str = "', '".join(str(p) for p in dir_paths)
            raise FileFormatError(
                f"Cannot put more than one directory, {dir_paths_str}, as part "
                f"of the same file group {self}"
            )
        # Make a copy of the file-group to validate the local paths and auto-gen
        # any defaults before they are pushed to the store
        cpy = copy(self)
        cpy.exists = True
        cpy.set_fs_paths(fs_paths)
        cache_paths = self.row.dataset.store.put_file_group_paths(self, cpy.fs_paths)
        # Set the paths to the cached files
        self.exists = True
        self.set_fs_paths(cache_paths)
        self.validate_file_paths()
        # Save provenance
        if self.provenance:
            self.row.dataset.store.put_provenance(self)

    @property
    def fs_paths(self):
        """All base paths (i.e. not nested within directories) in the file group"""
        if self.fs_path is None:
            raise FilePathsNotSetException(
                f"Attempting to access file path of {self} before it is set"
            )
        return [self.fs_path]

    @classmethod
    def fs_names(cls):
        """Return names for each top-level file-system path in the file group,
        used when generating Pydra task interfaces.

        Returns
        -------
        tuple[str]
            sequence of names for top-level file-system paths in the file group"""
        return ("fs_path",)

    @classmethod
    def matches_format_name(cls, name: str):
        """Checks to see whether the provided name is a valid name for the
        file format. Alternative names can be provided for format-specific
        subclasses, or this method can be overridden. Matches are case
        insensitive.

        Parameters
        ----------
        name : str
            Name to match

        Returns
        -------
        bool
            whether or not the name matches the datatype
        """
        return name.lower() in [
            n.lower() for n in (cls.class_name(),) + cls.alternative_names
        ]

    @property
    def value(self):
        return str(self.fs_path)

    @property
    def checksums(self):
        if self._checksums is None:
            self.get_checksums()
        return self._checksums

    def get_checksums(self, force_calculate=False):
        self._check_exists()
        # Load checksums from store (e.g. via API)
        if self.row is not None and not force_calculate:
            self._checksums = self.row.dataset.store.get_checksums(self)
        # If the store cannot calculate the checksums do them manually
        else:
            self._checksums = self.calculate_checksums()

    def calculate_checksums(self):
        self._check_exists()
        checksums = {}
        for fpath in self.all_file_paths():
            fhash = hashlib.md5()
            with open(fpath, "rb") as f:
                # Calculate hash in chunks so we don't run out of memory for
                # large files.
                for chunk in iter(lambda: f.read(HASH_CHUNK_SIZE), b""):
                    fhash.update(chunk)
            checksums[fpath] = fhash.hexdigest()
        checksums = self.generalise_checksum_keys(checksums)
        return checksums

    def contents_equal(self, other, **kwargs):
        """
        Test the equality of the file_group contents with another file_group.
        If the file_group's format implements a 'contents_equal' method than
        that is used to determine the equality, otherwise a straight comparison
        of the checksums is used.

        Parameters
        ----------
        other : FileGroup
            The other file_group to compare to
        """
        self._check_exists()
        other._check_exists()
        return self.checksums[self.fs_path.name] == other.checksums[other.fs_path.name]

    @classmethod
    def resolve(cls, unresolved):
        """Resolve file group loaded from a repository to the specific datatype

        Parameters
        ----------
        unresolved : UnresolvedFileGroup
            A file group loaded from a repository that has not been resolved to
            a specific datatype yet

        Returns
        -------
        FileGroup
            The resolved file-group object

        Raises
        ------
        ArcanaUnresolvableFormatException
            If there doesn't exist a unique resolution from the unresolved file
            group to the given datatype, then an FileFormatError should be
            raised
        """
        # Perform matching based on resource names in multi-datatype
        # file-group
        if unresolved.uris is not None:
            item = None
            for format_name, uri in unresolved.uris.items():
                if cls.matches_format_name(format_name):
                    item = cls(uri=uri, **unresolved.item_kwargs)
            if item is None:
                raise FileFormatError(
                    f"Could not file a matching resource in {unresolved.path} for"
                    f" the given datatype ({cls.class_name()}), found "
                    "('{}')".format("', '".join(unresolved.uris))
                )
        else:
            item = cls(**unresolved.item_kwargs)
            item.set_fs_paths(unresolved.file_paths)
        return item

    @abstractmethod
    def set_fs_paths(self, fs_paths: ty.List[Path]):
        """Set the file paths of the file group

        Parameters
        ----------
        fs_paths : list[Path]
            The candidate paths from which to set the paths of the
            file group from. Note that not all paths need to be set if
            they are not relevant.

        Raises
        ------
        FileFormatError
            is raised if the required the paths cannot be set from the provided
        """

    @classmethod
    def from_fs_paths(cls, *fs_paths: ty.List[Path], path=None):
        """Create a FileGroup object from a set of file-system paths

        Parameters
        ----------
        fs_paths : list[Path]
            The candidate paths from which to set the paths of the
            file group from. Note that not all paths need to be set if
            they are not relevant.
        path : str, optional
            the location of the file-group relative to the node it (will)
            belong to. Defaults to

        Returns
        -------
        FileGroup
            The created file-group
        """
        if path is None:
            path = fs_paths[0].stem
        obj = cls(path)
        obj.set_fs_paths(fs_paths)
        return obj

    @classmethod
    def matches_ext(cls, *paths, ext=None):
        """Returns the path out of the candidates provided that matches the
        given extension (by default the extension of the class)

        Parameters
        ----------
        *paths: list[Path]
            The paths to select from
        ext: str or None
            the extension to match (defaults to 'ext' attribute of class)

        Returns
        -------
        Path
            the matching path

        Raises
        ------
        FileFormatError
            When no paths match or more than one path matches the given extension"""
        if ext is None:
            ext = cls.ext
        if ext:
            matches = [str(p) for p in paths if str(p).endswith("." + ext)]
        else:
            matches = paths
        if not matches:
            paths_str = ", ".join(str(p) for p in paths)
            raise FileFormatError(
                f"No matching files with '{ext}' extension found in "
                f"file group {paths_str}"
            )
        elif len(matches) > 1:
            matches_str = ", ".join(str(p) for p in matches)
            raise FileFormatError(
                f"Multiple files with '{ext}' extension found in : {matches_str}"
            )
        return str(matches[0])

    def validate_file_paths(self):
        attrs.validate(self)
        self.exists = True

    def _check_paths_exist(self, fs_paths: ty.List[Path]):
        if missing := [p for p in fs_paths if not p or not Path(p).exists()]:
            missing_str = "\n".join(str(p) for p in missing)
            all_str = "\n".join(str(p) for p in fs_paths)
            msg = (
                f"The following file system paths provided to {self} do not "
                f"exist:\n{missing_str}\n\nFrom full list:\n{all_str}"
            )
            for fs_path in missing:
                if fs_path:
                    if fs_path.parent.exists():
                        msg += (
                            f"\n\nFiles in the directory '{str(fs_path.parent)}' are:\n"
                        )
                        msg += "\n".join(str(p) for p in fs_path.parent.iterdir())
            raise FileFormatError(msg)

    def convert_to(self, to_format, **kwargs):
        """Convert the FileGroup to a new datatype

        Parameters
        ----------
        to_format : type
            the file-group datatype to convert to
        **kwargs
            args to pass to the conversion process

        Returns
        -------
        FileGroup
            the converted file-group
        """
        task = to_format.converter_task(
            from_format=type(self), name="converter", **kwargs
        )
        task.inputs.to_convert = self
        result = task(plugin="serial")
        return result.output.converted

    @classmethod
    def converter_task(cls, from_format, name, **kwargs):
        """Adds a converter row to a workflow

        Parameters
        ----------
        from_format : type
            the file-group class to convert from
        taks_name: str
            the name for the converter task
        **kwargs: dict[str, ty.Any]
            keyword arguments passed through to the converter

        Returns
        -------
        Workflow
            Pydra workflow to perform the conversion with an input called
            'to_convert' and an output called 'converted', which take and
            produce file-groups in `from_format` and `cls` types respectively.
        """

        wf = Workflow(name=name, input_spec=["to_convert"])

        # Get row to extract paths from file-group lazy field
        wf.add(
            func_task(
                access_paths,
                in_fields=[("from_format", type), ("file_group", from_format)],
                out_fields=[(i, Path) for i in from_format.fs_names()],
                # name='extract',
                from_format=from_format,
                file_group=wf.lzin.to_convert,
            )
        )

        # Aggregate converter inputs and combine with fixed keyword args
        conv_inputs = {
            n: getattr(wf.access_paths.lzout, n) for n in from_format.fs_names()
        }
        conv_inputs.update(kwargs)
        # Create converter node
        converter, output_lfs = cls.find_converter(from_format)(**conv_inputs)
        # If there is only one output lazy field, place it in a tuple so it can
        # be zipped with cls.fs_names()
        if isinstance(output_lfs, LazyField):
            output_lfs = (output_lfs,)
        # converter.name = 'converter'
        # for lf in output_lfs:
        #     lf.name = 'converter'
        wf.add(converter)

        # Encapsulate output paths from converter back into a file group object
        to_encapsulate = dict(zip(cls.fs_names(), output_lfs))

        logger.debug("Paths to encapsulate are:\n%s", to_encapsulate)

        wf.add(
            func_task(
                encapsulate_paths,
                in_fields=[("to_format", type), ("to_convert", from_format)]
                + [(o, ty.Union[str, Path]) for o in cls.fs_names()],
                out_fields=[("converted", cls)],
                # name='encapsulate',
                to_format=cls,
                to_convert=wf.lzin.to_convert,
                **to_encapsulate,
            )
        )

        wf.set_output(("converted", wf.encapsulate_paths.lzout.converted))

        return wf

    @classmethod
    def find_converter(cls, from_format):
        """Selects the converter method from the given datatype. Will select the
        most specific conversion.

        Parameters
        ----------
        from_format : type
            The datatype type to convert from

        Returns
        -------
        function or NoneType
            The bound method that adds rows to a given workflow if conversion is required
            and None if no conversion is required

        Raises
        ------
        FileFormatConversionError
            _description_
        """
        if from_format is cls or issubclass(from_format, cls):
            return None  # No conversion is required
        converter = None
        for attr_name in dir(cls):
            meth = getattr(cls, attr_name)
            try:
                converts_from = meth.__annotations__[CONVERTER_ANNOTATIONS]
            except (AttributeError, KeyError):
                pass
            else:
                if from_format is converts_from or issubclass(
                    from_format, converts_from
                ):
                    if converter:
                        prev_converts_from = converter.__annotations__[
                            CONVERTER_ANNOTATIONS
                        ]
                        if issubclass(converts_from, prev_converts_from):
                            converter = meth
                        elif not issubclass(prev_converts_from, converts_from):
                            raise FileFormatConversionError(
                                f"Ambiguous converters between {from_format} "
                                f"and {cls}: {converter} and {meth}. Please "
                                f"define a specific converter from {from_format} "
                                f"(i.e. instead of from {prev_converts_from} "
                                f"and {converts_from} respectively)"
                            )
                    else:
                        converter = meth
        if converter is None:
            raise FileFormatConversionError(
                f"No datatype converters are defined from {from_format} to {cls}"
            )
        return converter

    def generalise_checksum_keys(
        self, checksums: ty.Dict[str, str], base_path: Path = None
    ):
        """Generalises the paths used for the file paths in a checksum dictionary
        so that they are the same irrespective of that the top-level file-system
        paths are

        Parameters
        ----------
        checksums: dict[str, str]
            The checksum dict mapping relative file paths to checksums

        Returns
        -------
        dict[str, str]
            The checksum dict with file paths generalised"""
        if base_path is None:
            base_path = self.fs_path
        return {str(Path(k).relative_to(base_path)): v for k, v in checksums.items()}

    @classmethod
    def access_contents_task(cls, file_group_lf: LazyField):
        """Access the fs paths of the file group"""

    @classmethod
    def from_fs_path(cls, fs_path):
        file_group = cls(path=Path(fs_path).stem)
        file_group.set_fs_paths([fs_path])
        return file_group

    @classmethod
    def append_ext(cls, path: Path):
        if path.ext is not None:
            path = path.with_suffix(cls.ext)
        return path

    @classmethod
    def all_exts(cls):
        return [""]


def access_paths(from_format, file_group):
    """Copies files into the CWD renaming so the basenames match
    except for extensions"""
    logger.debug(
        "Extracting paths from %s (%s format) before conversion",
        file_group,
        from_format,
    )
    cpy = file_group.copy_to(path2varname(file_group.path), symlink=True)
    return cpy.fs_paths if len(cpy.fs_paths) > 1 else cpy.fs_path


def encapsulate_paths(
    to_format: type, to_convert: FileGroup, **fs_paths: ty.List[Path]
):
    """Copies files into the CWD renaming so the basenames match
    except for extensions"""
    logger.debug(
        "Encapsulating %s into %s format after conversion", fs_paths, to_format
    )
    file_group = to_format(to_convert.path + "_" + to_format.class_name())
    file_group.set_fs_paths(fs_paths.values())
    return file_group


@attrs.define
class Field(DataType):
    """
    A representation of a value field in the dataset.

    Parameters
    ----------
    name_path : str
        The name_path to the relative location of the field, i.e. excluding
        information about which row in the data tree it belongs to
    derived : bool
        Whether or not the value belongs in the derived session or not
    row : DataRow
        The data row that the field belongs to
    exists : bool
        Whether the field exists or is just a placeholder for a sink
    provenance : Provenance | None
        The provenance for the pipeline that generated the field,
        if applicable
    """

    value: ty.Any = None

    def get(self, assume_exists=False):
        if not assume_exists:
            self._check_exists()
        self._check_part_of_row()
        self.value = self.row.dataset.store.get_field_value(self)

    def put(self, value):
        self._check_part_of_row()
        self.row.dataset.store.put_field_value(self, self.format(value))
        self.exists = True

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __str__(self):
        if self.datatype.__args__:  # Sequence type
            val = "[" + ",".join(self._to_str(v) for v in self.value) + "]"
        else:
            val = self._to_str(self.value)
        return val

    def _to_str(self, val):
        if self.datatype is str:
            val = '"{}"'.format(val)
        else:
            val = str(val)
        return val

    def get_checksums(self):
        """
        For duck-typing with file_groups in checksum management. Instead of a
        checksum, just the value of the field is used
        """
        return self.value
