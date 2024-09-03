import typing as ty
from pathlib import Path
from typing_extensions import TypeAlias

if ty.TYPE_CHECKING:
    import fileformats.core

CryptoMethod: TypeAlias = ty.Optional[ty.Callable[[], ty.Any]]

FspathsInputType: TypeAlias = ty.Union[  # noqa: F821
    ty.Iterable[ty.Union[str, Path]],
    str,
    Path,
    "fileformats.core.FileSet",
]
