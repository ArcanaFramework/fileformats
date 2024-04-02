from pathlib import Path
from fileformats.core.fileset import FileSet
from fileformats.core.exceptions import (
    FormatMismatchError,
    UnconstrainedExtensionException,
)
from fileformats.core import hook
from fileformats.core.utils import classproperty
from .fsobject import FsObject


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

    def read_bytes(self, *args, **kwargs):
        return self.fspath.read_bytes(*args, **kwargs)

    def read_text(self, *args, **kwargs):
        if self.binary:
            raise FormatMismatchError(f"Cannot read text from binary filetype {self}")
        return self.fspath.read_text(*args, **kwargs)
