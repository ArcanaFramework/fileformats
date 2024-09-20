import typing as ty
import itertools
from pathlib import Path
from fileformats.core import FileSet, validated_property
from fileformats.core.mixin import WithClassifiers
from fileformats.core.collection import TypedCollection
from fileformats.core.exceptions import FormatMismatchError


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

    @validated_property
    def _all_paths_used(self) -> None:
        all_contents_paths = set(itertools.chain(*(c.fspaths for c in self.contents)))
        missing = self.fspaths - all_contents_paths
        if missing:
            contents_str = "\n".join(repr(c) for c in self.contents)
            raise FormatMismatchError(
                f"Paths {[str(p) for p in missing]} are not used by any of the "
                f"contents of {self.type_name}:\n{contents_str}"
            )


class SetOf(WithClassifiers, TypedSet):  # type: ignore[misc]
    # WithClassifiers-required class attrs
    classifiers_attr_name = "content_types"
    allowed_classifiers = (FileSet,)
    allow_optional_classifiers = True
    generically_classifiable = True
