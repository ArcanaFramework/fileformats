import typing as ty
import itertools
from pathlib import Path
from fileformats.core import FileSet
from fileformats.core.mixin import WithClassifiers
from fileformats.core.collection import TypedCollection


class TypedSet(TypedCollection):
    """List of specific file types (similar to the contents of a directory but not
    enclosed in one)"""

    MAX_REPR_PATHS = 3

    @property
    def content_fspaths(self) -> ty.Iterable[Path]:
        return self.fspaths

    def __repr__(self) -> str:
        paths_repr = (
            "'"
            + "', '".join(str(p) for p in sorted(self.fspaths)[: self.MAX_REPR_PATHS])
            + "'"
        )
        if len(self.fspaths) > self.MAX_REPR_PATHS:
            paths_repr += ", ..."
        return f"{self.type_name}({paths_repr})"

    def required_paths(self) -> ty.FrozenSet[Path]:
        return frozenset(itertools.chain(*(c.required_paths() for c in self.contents)))


class SetOf(WithClassifiers, TypedSet):  # type: ignore[misc]
    # WithClassifiers-required class attrs
    classifiers_attr_name = "content_types"
    allowed_classifiers = (FileSet,)
    allow_optional_classifiers = True
    generically_classifiable = True
