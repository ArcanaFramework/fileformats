from __future__ import annotations
import os
from pathlib import Path
import typing as ty
from itertools import chain
from copy import copy
import shutil
import attrs
from .exceptions import (
    FileFormatError,
)
from .base import FileGroup, absolute_path


@attrs.define
class BaseDirectory(FileGroup):

    is_dir = True
    content_types = ()  # By default, don't check contents for any types

    def set_fs_paths(self, fs_paths: ty.List[Path]):
        self._check_paths_exist(fs_paths)
        matches = [p for p in fs_paths if Path(p).is_dir() and self.contents_match(p)]
        types_str = ", ".join(t.__name__ for t in self.content_types)
        if not matches:
            raise FileFormatError(
                f"No matching directories with contents matching {types_str} amongst "
                f"{fs_paths}"
            )
        elif len(matches) > 1:
            matches_str = ", ".join(str(m) for m in matches)
            raise FileFormatError(
                f"Multiple directories with contents matching {types_str}: "
                f"{matches_str}"
            )
        self.exists = True
        self.fs_path = absolute_path(matches[0])

    @classmethod
    def contents_match(cls, path: Path):
        from arcana.core.data.row import UnresolvedFileGroup

        path = Path(path)  # Ensure a Path object not a string
        contents = UnresolvedFileGroup.from_paths(path, path.iterdir())
        for content_type in cls.content_types:
            resolved = False
            for unresolved in contents:
                try:
                    content_type.resolve(unresolved)
                except FileFormatError:
                    pass
                else:
                    resolved = True
                    break
            if not resolved:
                return False
        return True

    def all_file_paths(self):
        "Iterates through all files in the group and returns their file paths"
        if self.fs_path is None:
            raise RuntimeError(
                f"Attempting to access file paths of {self} before they are set"
            )
        return chain(
            *(
                (Path(root) / f for f in files)
                for root, _, files in os.walk(self.fs_path)
            )
        )

    def copy_to(self, fs_path: str, symlink: bool = False):
        """Copies the file-group to the new path, with auxiliary files saved
        alongside the primary-file path.

        Parameters
        ----------
        fs_path : str
            Path to save the file-group to excluding file extensions
        symlink : bool
            Use symbolic links instead of copying files to new location
        """
        if symlink:
            copy_dir = os.symlink
        else:
            copy_dir = shutil.copytree
        copy_dir(self.fs_path, fs_path)
        cpy = copy(self)
        cpy.set_fs_paths([fs_path])
        return cpy
