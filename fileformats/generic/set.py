import typing as ty
from fileformats.core import FileSet, validated_property
from functools import cached_property
from fileformats.core.mixin import WithClassifiers


class TypedSet(FileSet):
    """List of specific file types (similar to the contents of a directory but not
    enclosed in one)"""

    content_types: ty.Tuple[ty.Type[FileSet], ...] = ()

    MAX_REPR_PATHS = 3

    def __repr__(self) -> str:
        paths_repr = (
            "'"
            + "', '".join(str(p) for p in sorted(self.fspaths)[: self.MAX_REPR_PATHS])
            + "'"
        )
        if len(self.fspaths) > self.MAX_REPR_PATHS:
            paths_repr += ", ..."
        return f"{self.type_name}({paths_repr})"

    @cached_property
    def contents(self) -> ty.List[FileSet]:  # type: ignore[override]
        contnts = []
        for content_type in self.content_types:
            for p in self.fspaths:
                contnts.append(content_type([p], **self._metadata_kwargs))
        return contnts

    @validated_property
    def _validate_contents(self) -> None:
        self.contents


class SetOf(WithClassifiers, TypedSet):
    # WithClassifiers-required class attrs
    classifiers_attr_name = "content_types"
    allowed_classifiers = (FileSet,)
    generically_classifiable = True
