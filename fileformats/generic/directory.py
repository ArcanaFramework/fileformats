import typing as ty
from pathlib import Path
from fileformats.core.exceptions import FormatMismatchError
from fileformats.core import hook
from fileformats.core.utils import classproperty
from .fsobject import FsObject
from fileformats.core.fileset import FileSet
from fileformats.core.mixin import WithClassifiers


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

    # Duck-type Path methods

    def __div__(self, other: ty.Union[str, Path]) -> Path:
        return self.fspath / other

    def glob(self, pattern):
        return self.fspath.glob(pattern)

    def rglob(self, pattern):
        return self.fspath.rglob(pattern)

    def joinpath(self, *args, **kwargs):
        return self.fspath.joinpath(*args, **kwargs)

    def iterdir(self):
        return self.fspath.iterdir()


class DirectoryContaining(WithClassifiers, Directory):
    """Generic directory classified by the formats of its contents"""

    # WithClassifiers-required class attrs
    classifiers_attr_name = "content_types"
    allowed_classifiers = (FileSet,)
    generically_classifies = True
