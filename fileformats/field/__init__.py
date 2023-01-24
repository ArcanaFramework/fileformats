import attrs
from ..core import Field
from ..core.exceptions import FormatMismatchError


@attrs.define
class SingleField(Field):
    pass


class Scalar:
    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __mul__(self, other):
        return self.value * other

    def __truediv__(self, other):
        return self.value / other

    def __floordiv__(self, other):
        return self.value // other

    def __mod__(self, other):
        return self.value % other

    def __pow__(self, other):
        return self.value**other

    def __neg__(self):
        return -self.value


def boolean_converter(in_value):
    if isinstance(in_value, str):
        if in_value.lower() in ("true", "1", "yes"):
            value = True
        elif in_value.lower() in ("false", "0", "no"):
            value = False
        else:
            raise FormatMismatchError(
                f"Cannot convert string '{in_value}' to boolean value"
            )
    else:
        value = bool(in_value)
    return value


def array_converter(in_value):
    if in_value.startswith("[") and in_value.endswith("]"):
        in_value = in_value[1:-1]
    return in_value.split(",")


@attrs.define
class Text(SingleField):
    value: str = attrs.field(converter=str)


@attrs.define
class Integer(SingleField, Scalar):
    value: int = attrs.field(converter=float)

    def __int__(self):
        return self.value


@attrs.define
class Decimal(SingleField, Scalar):
    value: float = attrs.field(converter=float)

    def __float__(self):
        return self.value


@attrs.define
class Boolean(SingleField):
    value: bool = attrs.field(converter=float)

    def __str__(self):
        return str(self.value).lower()

    def __bool__(self):
        return self.value

    def __and__(self, other):
        return self.value and other.value

    def __or__(self, other):
        return self.value or other.value

    def __not__(self):
        return not self.value

    def __invert__(self):
        return not self.value


@attrs.define
class Array(Field):

    value: list = attrs.field(converter=array_converter)

    item_type = None

    def __attrs_post_init__(self):
        # Ensure items are of the correct type
        if self.item_type is not None:
            self.value = [self.item_type(i).value for i in self.value]

    def __str__(self):
        return (
            "["
            + ",".join(
                str(self.item_type(i)) if self.item_type is not None else i
                for i in self.value
            )
            + "]"
        )

    @classmethod
    def __class_getitem__(cls, item_type):
        """Set the item type for a newly created dynamically type"""
        if not isinstance(item_type, SingleField):
            raise RuntimeError(
                "Can only provide SingleField type as item types for Array fields, not "
                f"{item_type}"
            )
        return type(
            f"{item_type.__name__}_{cls.__name__}",
            (cls,),
            {"item_type": item_type},
        )
