import typing as ty
from fileformats.core import FileSet, validated_property
from functools import cached_property
from fileformats.core.exceptions import (
    FormatMismatchError,
)
from fileformats.core.mixin import WithClassifiers


class TypedSet(FileSet):
    """List of specific file types (similar to the contents of a directory but not
    enclosed in one)"""

    content_types: ty.Tuple[ty.Type[FileSet], ...] = ()

    @cached_property
    def contents(self) -> ty.List[FileSet]:
        contnts = []
        for content_type in self.content_types:
            for p in self.fspaths:
                try:
                    contnts.append(content_type([p], **self._metadata_kwargs))
                except FormatMismatchError:
                    continue
        return contnts

    @validated_property
    def _validate_contents(self) -> None:
        if not self.content_types:
            return
        not_found = set(self.content_types)
        for fspath in self.fspaths:
            for content_type in list(not_found):
                if content_type.matches(fspath):
                    not_found.remove(content_type)
                    if not not_found:
                        return
        assert not_found
        raise FormatMismatchError(
            f"Did not find the required content types, {not_found}, within the "
            f"given list {self.fspaths}"
        )


class SetOf(WithClassifiers, TypedSet):
    # WithClassifiers-required class attrs
    classifiers_attr_name = "content_types"
    allowed_classifiers = (FileSet,)
    generically_classifiable = True
