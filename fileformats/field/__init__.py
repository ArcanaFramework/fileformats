import attrs
from ..core import Field
from ..core.exceptions import FormatMismatchError


@attrs.define
class Singluar(Field):
    pass


class LogicalMixin:
    def __bool__(self):
        return bool(self.value)

    def __and__(self, other):
        return self.value and other.value

    def __or__(self, other):
        return self.value or other.value

    def __not__(self):
        return not self.value

    def __invert__(self):
        return not self.value


class ScalarMixin(LogicalMixin):
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

    def __pos__(self):
        return +self.value

    def __abs__(self):
        return abs(self.value)


def text_converter(value):
    try:
        return str(value)
    except ValueError as e:
        raise FormatMismatchError(str(e))


def integer_converter(value):
    if isinstance(value, float):
        raise FormatMismatchError(
            f"Cannot convert float ({value}) to integer field without potential loss "
            "of information"
        )
    try:
        return int(value)
    except ValueError as e:
        raise FormatMismatchError(str(e))


def decimal_converter(value):
    try:
        return float(value)
    except ValueError as e:
        raise FormatMismatchError(str(e))


def boolean_converter(value):
    if isinstance(value, str):
        if value.lower() in ("true", "1", "yes"):
            value = True
        elif value.lower() in ("false", "0", "no"):
            value = False
        else:
            raise FormatMismatchError(
                f"Cannot convert string '{value}' to boolean value"
            )
    else:
        try:
            value = bool(value)
        except ValueError as e:
            raise FormatMismatchError(str(e))
    return value


def array_converter(value):
    if isinstance(value, str):
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]
        elif value.startswith("[") or value.endswith("]"):
            raise FormatMismatchError(f"Unmatched brackets in array field {value}")
        value = [v.strip() for v in value.split(",")]
    else:
        try:
            value = list(value)
        except ValueError as e:
            raise FormatMismatchError(str(e))
    return value


@attrs.define
class Text(Singluar):

    value: str = attrs.field(converter=text_converter)

    type = str


@attrs.define
class Integer(Singluar, ScalarMixin):

    value: int = attrs.field(converter=integer_converter)

    type = int

    def __int__(self):
        return self.value


@attrs.define
class Decimal(Singluar, ScalarMixin):

    value: float = attrs.field(converter=decimal_converter)

    type = int

    def __float__(self):
        return self.value


@attrs.define
class Boolean(Singluar, LogicalMixin):

    value: bool = attrs.field(converter=boolean_converter)

    type = bool

    def __str__(self):
        return str(self.value).lower()

    def __bool__(self):
        return self.value


@attrs.define
class Array(Field):

    value: list = attrs.field(converter=array_converter)

    item_type = None

    type = list

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

    def __iter__(self):
        return iter(self.value)

    @classmethod
    def __class_getitem__(cls, item_type):
        """Set the item type for a newly created dynamically type"""
        if not issubclass(item_type, Singluar):
            raise RuntimeError(
                'Can only provide "Singluar" field type as item types for Array fields, not '
                f"{item_type}"
            )
        return type(
            f"{item_type.__name__}_{cls.__name__}",
            (cls,),
            {"item_type": item_type},
        )
