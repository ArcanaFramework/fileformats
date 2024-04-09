from __future__ import annotations
import typing as ty
from .utils import (
    classproperty,
)
from .datatype import DataType
from .exceptions import FormatMismatchError


class Field(DataType):
    """Base class for all field formats"""

    type = None
    is_field = True
    primitive = None
    metadata = None  # Empty metadata dict for duck-typing with file-sets

    def __init__(self, value):
        self.value = value

    def __eq__(self, field) -> bool:
        return (
            isinstance(field, Field)
            and self.mime_like == field.mime_like
            and self.value == field.value
        )

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash((self.mime_like, self.value))

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.type_name}({str(self)})"

    @classproperty
    def all_fields(cls) -> ty.List[ty.Type[Field]]:  # pylint: disable=no-self-argument
        """Iterate over all field formats in fileformats.* namespaces"""
        import fileformats.field  # noqa

        return [f for f in Field.subclasses() if f.primitive is not None]

    @classmethod
    def from_primitive(cls, dtype: type):
        try:
            datatype = next(iter(f for f in cls.all_fields if f.primitive is dtype))
        except StopIteration as e:
            field_types_str = ", ".join(t.__name__ for t in cls.all_fields)
            raise FormatMismatchError(
                f"{dtype} doesn't not correspond to a valid fileformats field type "
                f"({field_types_str})"
            ) from e
        return datatype

    _all_fields = None
