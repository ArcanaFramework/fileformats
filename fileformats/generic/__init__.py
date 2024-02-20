import os
import random
import typing as ty
import string
import itertools
from random import Random
from pathlib import Path
from fileformats.core.fileset import FileSet
from fileformats.core.exceptions import (
    FormatMismatchError,
    UnconstrainedExtensionException,
)
from fileformats.core import hook
from fileformats.core.utils import classproperty, SampleFileGenerator
from fileformats.core.mixin import WithClassifiers


class FsObject(FileSet, os.PathLike):
    "Generic file-system object, can be either a file or a directory"

    @hook.required
    @property
    def fspath(self):
        if len(self.fspaths) > 1:
            raise FormatMismatchError(
                f"More than one fspath ({self.fspaths}) provided to {self}, "
                f"primary path is ambiguous"
            )
        return next(iter(self.fspaths))

    def __str__(self):
        return str(self.fspath)

    def __fspath__(self):
        """Render to string, so can be treated as any other file-system path, i.e. passed
        to functions like file 'open'"""
        return str(self)

    @property
    def stem(self):
        return self.fspath.with_suffix("").name

    @classproperty
    def unconstrained(cls) -> bool:
        """Whether the file-format is unconstrained by extension, magic number or another
        constraint"""
        # We have to subtract `fspath` from required properties as we defined unconstrained
        # file-sets as ones that have more constraints than simply existing
        return not (len(list(cls.required_properties())) - 1)


class File(FsObject):
    """Generic file type"""

    binary = True
    is_dir = False

    @hook.required
    @property
    def fspath(self):
        fspath = self.select_by_ext()
        if fspath.is_dir():
            # fspath is guaranteed to exist
            raise FormatMismatchError(
                f'Path that matches extension of {type(self)}, "{fspath}", '
                f"is a directory not a file"
            )
        return fspath

    @classproperty
    def unconstrained(cls) -> bool:
        """Whether the file-format is unconstrained by extension, magic number or another
        constraint"""
        return super().unconstrained and (cls.ext is None or None in cls.alternate_exts)

    @classmethod
    def copy_ext(
        cls,
        old_path: Path,
        new_path: Path,
        decomposition_mode=FileSet.ExtensionDecomposition.none,
    ):
        """Copy extension from the old path to the new path, ensuring that all
        of the extension is used (e.g. 'my.gz' instead of 'gz')

        Parameters
        ----------
        old_path: Path or str
            The path from which to copy the extension from
        new_path: Path or str
            The path to append the extension to
        decomposition_mode : FileSet.ExtensionDecomposition, optional
            if the file doesn't have an explicit extension, how to interpret "." within
            the filename

        Returns
        -------
        Path
            The new path with the copied extension
        """
        if not cls.matching_exts([old_path], [cls.ext]):
            raise FormatMismatchError(
                f"Extension of old path ('{str(old_path)}') does not match that "
                f"of file, '{cls.ext}'"
            )
        suffix = (
            cls.ext
            if cls.ext
            else cls.decompose_fspath(old_path, mode=decomposition_mode)[-1]
        )
        return Path(new_path).with_suffix(suffix)

    @property
    def contents(self):
        return self.read_contents()

    def read_contents(self, size=None, offset=0):
        with open(self.fspath, "rb" if self.binary else "r") as f:
            if offset:
                f.read(offset)
            contents = f.read(size)
        return contents

    @property
    def actual_ext(self):
        "The actual file extension (out of the primary  and alternate extensions possible)"
        constrained_exts = [
            e for e in self.possible_exts if e is not None
        ]  # strip out unconstrained
        matching = [e for e in constrained_exts if self.fspath.name.endswith(e)]
        if not matching:
            raise UnconstrainedExtensionException(
                f"Cannot determine actual extension of {self.fspath}, as it doesn't "
                f"match any of the defined extensions {constrained_exts} "
                "(i.e. matches the None extension)"
            )
        # Return the longest matching extension, useful for optional extensions
        return sorted(matching, key=len)[-1]

    @property
    def stem(self):
        if self.actual_ext:
            stem = self.fspath.name[: -len(self.actual_ext)]
        else:
            stem = self.fspath
        return stem


class Directory(FsObject):
    """Base directory to be overridden by subtypes that represent directories but don't
    want to inherit content type "qualifers" (i.e. most of them)"""

    is_dir = True

    content_types = ()

    @hook.required
    @property
    def fspath(self):
        # fspaths are checked for existence with the exception of mock classes
        dirs = [p for p in self.fspaths if not p.is_file()]
        if not dirs:
            raise FormatMismatchError(f"No directory paths provided {repr(self)}")
        if len(dirs) > 1:
            raise FormatMismatchError(
                f"More than one directory path provided {dirs} to {repr(self)}"
            )
        fspath = dirs[0]
        missing = []
        for content_type in self.content_types:
            match = False
            for p in fspath.iterdir():
                try:
                    content_type([p])
                except FormatMismatchError:
                    continue
                else:
                    match = True
                    break
            if not match:
                missing.append(content_type)
        if missing:
            raise FormatMismatchError(
                f"Did not find matches for {missing} content types in {repr(self)}"
            )
        return fspath

    @property
    def contents(self):
        for content_type in self.content_types:
            for p in self.fspath.iterdir():
                try:
                    yield content_type([p])
                except FormatMismatchError:
                    continue

    @classproperty
    def unconstrained(cls) -> bool:
        """Whether the file-format is unconstrained by extension, magic number or another
        constraint"""
        return super().unconstrained and not cls.content_types

    @hook.check
    def validate_contents(self):
        if not self.content_types:
            return
        not_found = set(self.content_types)
        for fspath in self.fspath.iterdir():
            for content_type in list(not_found):
                if content_type.matches(fspath):
                    not_found.remove(content_type)
                    if not not_found:
                        return
        assert not_found
        raise FormatMismatchError(
            f"Did not find the required content types, {not_found}, within the "
            f"directory {self.fspath} of {self}"
        )

    def hash_files(self, relative_to=None, **kwargs):
        if relative_to is None:
            relative_to = self.fspath
        return super().hash_files(relative_to=relative_to, **kwargs)


class TypedSet(FileSet):
    """List of specific file types (similar to the contents of a directory but not
    enclosed in one)"""

    content_types = ()

    @property
    def contents(self):
        for content_type in self.content_types:
            for p in self.fspaths:
                try:
                    yield content_type([p])
                except FormatMismatchError:
                    continue

    @hook.check
    def validate_contents(self):
        if not self.content_types:
            return
        not_found = set(self.content_types)
        for fspath in self.fspaths:
            for content_type in list(not_found):
                if content_type.matches(fspath):
                    not_found.remove(content_type)
                    if not not_found:
                        return
        assert not_found
        raise FormatMismatchError(
            f"Did not find the required content types, {not_found}, within the "
            f"given list {self.fspaths}"
        )


class DirectoryContaining(WithClassifiers, Directory):
    """Generic directory classified by the formats of its contents"""

    # WithClassifiers-required class attrs
    classifiers_attr_name = "content_types"
    allowed_classifiers = (FileSet,)
    generically_classifies = True


class SetOf(WithClassifiers, TypedSet):
    # WithClassifiers-required class attrs
    classifiers_attr_name = "content_types"
    allowed_classifiers = (FileSet,)
    generically_classifies = True


# Methods to generate sample files, typically used in testing
FILE_FILL_LENGTH = 256


@FileSet.generate_sample_data.register
def fsobject_generate_sample_data(
    fsobject: FsObject,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return [generator.generate(File, fill=FILE_FILL_LENGTH)]


@FileSet.generate_sample_data.register
def file_generate_sample_data(
    file: File,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    contents = None
    if file.binary:
        if hasattr(file, "magic_number"):
            offset = getattr(file, "magic_number_offset", 0)
            contents = os.urandom(offset)
            magic_number = getattr(file, "magic_number", b"")
            if isinstance(magic_number, str):
                magic_number = bytes.fromhex(magic_number)
            contents += magic_number
        elif hasattr(file, "magic_pattern"):
            raise NotImplementedError(
                "Sampling of magic version file types is not implemented yet"
            )
    fspaths = [generator.generate(file, contents=contents, fill=FILE_FILL_LENGTH)]
    if hasattr(file, "header_type"):
        fspaths.extend(file.header_type.sample_data(generator))
    if hasattr(file, "side_car_types"):
        for side_car_type in file.side_car_types:
            fspaths.extend(side_car_type.sample_data(generator))
    return fspaths


@FileSet.generate_sample_data.register
def directory_generate_sample_data(
    directory: Directory,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    a_dir = generator.generate_fspath(Directory)
    a_dir.mkdir()
    File.sample_data(
        generator.child(dest_dir=a_dir)
    )  # Add a sample file for good measure
    return [a_dir]


@FileSet.generate_sample_data.register
def directory_containing_generate_sample_data(
    directory: DirectoryContaining,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    a_dir = generator.generate_fspath(Directory)
    a_dir.mkdir()
    for tp in directory.content_types:
        tp.sample_data(generator.child(dest_dir=a_dir))
    return [a_dir]


@FileSet.generate_sample_data.register
def set_of_sample_data(
    set_of: SetOf,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return list(
        itertools.chain(
            *(tp.sample_data(generator.child()) for tp in set_of.content_types)
        )
    )
