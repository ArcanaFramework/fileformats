from __future__ import annotations
import os
from pathlib import Path
import attrs
from .base import FileSet
from .exceptions import FormatMismatchError
from . import mark
from .utils import splitext


@attrs.define
class File(FileSet, os.PathLike):
    """Generic file type"""

    ext = ""
    binary = False
    is_dir = False

    @mark.required
    @property
    def fspath(self):
        fspath = self.select_by_ext(self.ext)
        if not fspath.is_file():
            raise FormatMismatchError(
                f'Path that matches extension "{self.ext}", {fspath}, is not a file in '
                f"{repr(self)}"
            )
        return fspath

    def __str__(self):
        return str(self.fspath)

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
        if not cls.matching_ext([old_path], cls.ext):
            raise FormatMismatchError(
                f"Extension of old path ('{str(old_path)}') does not match that "
                f"of file, '{cls.ext}'"
            )
        suffix = cls.ext if cls.ext else splitext(old_path, multi=True)[-1]
        return Path(new_path).with_suffix(suffix)

    @property
    def contents(self):
        return self.read_contents()

    def read_contents(self, size=None):
        with open(self.fspath, "rb" if self.binary else "r") as f:
            contents = f.read(size)
        return contents

    def required_paths(self):
        for prop_name in self.required_properties():
            prop = getattr(self, prop_name)
            if prop in self.fspaths:
                yield prop

    def __fspath__(self):
        return str(self)


@attrs.define
class Directory(FileSet, os.PathLike):
    """Generic directory type"""

    content_types = ()
    is_dir = True

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
                    content_type.with_adjacents([p])
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
                    yield content_type.with_adjacents([p])
                except FormatMismatchError:
                    continue

    @mark.check
    def validate_contents(self):
        for content in self.contents:
            content.validate()

    @classmethod
    def __class_getitem__(cls, *content_types):
        """Set the content types for a newly created dynamically type"""
        content_type_str = "_".join(t.__name__ for t in content_types)
        return type(
            f"{cls.__name__}_containing_{content_type_str}",
            (cls,),
            {"content_types": content_types},
        )

    def __str__(self):
        return str(self.fspath)

    def __fspath__(self):
        return str(self)
