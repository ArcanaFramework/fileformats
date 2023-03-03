import os
from pathlib import Path
import attrs
from ..core.base import FileSet
from ..core.exceptions import FormatMismatchError, FileFormatsError
from ..core import mark
from ..core.utils import splitext, classproperty
from ..core.mixin import WithQualifiers


@attrs.define
class FsObject(FileSet, os.PathLike):
    "Generic file-system object, can be either a file or a directory"

    @mark.required
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


@attrs.define
class File(FsObject):
    """Generic file type"""

    binary = False
    is_dir = False

    @mark.required
    @property
    def fspath(self):
        fspath = self.select_by_ext()
        if not fspath.is_file():
            if not fspath.exists():
                msg = (
                    f"Selected fspath for {type(self)}, '{str(fspath)}', does not exist"
                )
                if fspath.parent.exists():
                    neighbours = [p.name for p in fspath.parent.iterdir()]
                    msg += f". Found neighbouring files {neighbours}"
                raise FileFormatsError(msg)
            else:
                msg = ", it is a directory" if fspath.is_dir() else ""
                raise FormatMismatchError(
                    f'Path that matches extension of "{type(self)}", {fspath}, is not a '
                    "file in {repr(self)}" + msg
                )
        return fspath

    @classmethod
    def copy_ext(cls, old_path: Path, new_path: Path):
        """Copy extension from the old path to the new path, ensuring that all
        of the extension is used (e.g. 'my.gz' instead of 'gz')

        Parameters
        ----------
        old_path: Path or str
            The path from which to copy the extension from
        new_path: Path or str
            The path to append the extension to

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
        suffix = cls.ext if cls.ext else splitext(old_path, multi=True)[-1]
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

    @classproperty
    def possible_exts(cls):
        possible = [cls.ext]
        try:
            possible.extend(cls.alternate_exts)
        except AttributeError:
            pass
        return possible

    @property
    def actual_ext(self):
        "The actual file extension (out of the primary  and alternate extensions possible)"
        matching = [e for e in self.possible_exts if self.fspath.name.endswith(e)]
        if not matching:
            assert False, (
                f"extension of fspath {self.fspath} is not in possible extensions for "
                f"{type(self)} class: {self.possible_exts}. This should have been "
                "checked at initialisation"
            )
        # Return the longest matching extension, useful for optional extensions
        return sorted(matching, key=lambda x: len(x))[-1]

    @property
    def stem(self):
        return self.fspath.name[: -len(self.actual_ext)]


@attrs.define
class Directory(FsObject):
    """Base directory to be overridden by subtypes that represent directories but don't
    want to inherit content type "qualifers" (i.e. most of them)"""

    is_dir = True

    content_types = ()

    @mark.required
    @property
    def fspath(self):
        dirs = [p for p in self.fspaths if p.is_dir()]
        if not dirs:
            raise FormatMismatchError(f"No directory paths provided {repr(self)}")
        elif len(dirs) > 1:
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

    @mark.check
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

    @mark.check
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


class DirectoryContaining(WithQualifiers, Directory):
    """Generic directory qualified by the formats of its contents"""

    # WithQualifiers-required class attrs
    qualifiers_attr_name = "content_types"
    allowed_qualifiers = (FileSet,)
    generically_qualifies = True


class SetOf(WithQualifiers, TypedSet):

    # WithQualifiers-required class attrs
    qualifiers_attr_name = "content_types"
    allowed_qualifiers = (FileSet,)
    generically_qualifies = True
