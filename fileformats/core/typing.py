import sys
import typing as ty
from pathlib import Path

if sys.version_info[:2] < (3, 11):
    from typing_extensions import TypeAlias, Self
else:
    from typing import TypeAlias, Self

if ty.TYPE_CHECKING:
    import fileformats.core

CryptoMethod: TypeAlias = ty.Optional[ty.Callable[[], ty.Any]]

FspathsInputType: TypeAlias = ty.Union[  # noqa: F821
    ty.Iterable[ty.Union[str, Path]],
    str,
    Path,
    "fileformats.core.FileSet",
]

PathType: TypeAlias = ty.Union[str, Path]


__all__ = [
    "CryptoMethod",
    "FspathsInputType",
    "PathType",
    "TypeAlias",
    "Self",
]
