from __future__ import annotations
import typing as ty
import attrs
from .utils import (
    classproperty,
)
from .exceptions import (
    FileFormatsError,
)
from .datatype import DataType


@attrs.define(repr=False)
class Field(DataType):
    value = attrs.field()

    type = None
    is_field = True
    primitive = None

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self._type_name}({str(self)})"

    @property
    def metadata(self):
        """Empty metadata dict for duck-typing with file-sets"""
        return {}

    @classproperty
    def all_fields(cls) -> list[ty.Type[Field]]:  # pylint: disable=no-self-argument
        """Iterate over all field formats in fileformats.* namespaces"""
        import fileformats.field  # noqa

        return [f for f in Field.subclasses() if f.primitive is not None]

    @classmethod
    def from_primitive(cls, dtype: type):
        try:
            datatype = next(iter(f for f in cls.all_fields if f.primitive is dtype))
        except StopIteration as e:
            field_types_str = ", ".join(t.__name__ for t in cls.all_fields)
            raise FileFormatsError(
                f"{dtype} doesn't not correspond to a valid fileformats field type "
                f"({field_types_str})"
            ) from e
        return datatype

    _all_fields = None
