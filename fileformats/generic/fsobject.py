import os
import typing as ty
from pathlib import Path
from fileformats.core.fileset import FileSet
from fileformats.core.exceptions import (
    FormatMismatchError,
)
from fileformats.core import hook
from fileformats.core.utils import classproperty


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

    def absolute(self) -> Path:
        return self.fspath

    @property
    def anchor(self) -> str:
        return self.fspath.anchor

    def chmod(self, mode: int, *, follow_symlinks: bool = True):
        return self.fspath.chmod(mode, follow_symlinks=follow_symlinks)

    @property
    def drive(self) -> str:
        return self.fspath.drive

    def exists(self) -> bool:
        return True

    def group(self) -> str:
        return self.fspath.group()

    def is_dir(self) -> bool:
        return self.fspath.is_dir()

    def is_file(self) -> bool:
        return self.fspath.is_file()

    @property
    def name(self) -> str:
        return self.fspath.name

    def open(self, *args, **kwargs):
        return self.fspath.open(*args, **kwargs)

    def owner(self) -> str:
        return self.fspath.owner()

    @property
    def parent(self) -> Path:
        return self.fspath.parent

    @property
    def parents(self) -> Path:
        return self.fspath.parents

    @property
    def parts(self) -> ty.List[str]:
        return self.fspath.parts

    @property
    def root(self) -> str:
        return self.fspath.root

    def stat(self, **kwargs) -> os.stat_result:
        return self.fspath.stat(**kwargs)

    @property
    def suffix(self) -> str:
        return self.fspath.suffix

    @property
    def suffixes(self):
        return self.fspath.suffixes
