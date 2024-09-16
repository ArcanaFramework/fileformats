import sys
import re
import typing as ty
from importlib import import_module
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


def eval_type(type_str: ty.Union[str, type]) -> type:
    """Evaluates a type string so it can be compared with the type it represents"""
    if not isinstance(type_str, str):
        return type_str
    module_match = re.match(r"((?:\w+\.)*).*", type_str)
    if module_match:
        mod_path = module_match.group(1)[:-1]
        import_module(mod_path)
    try:
        return eval(type_str)  # type: ignore[no-any-return]
    except Exception:
        raise ValueError(f"Could not evaluate '{type_str}' type")


__all__ = [
    "CryptoMethod",
    "FspathsInputType",
    "PathType",
    "TypeAlias",
    "Self",
    "eval_type",
]
