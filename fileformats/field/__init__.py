"""Adds support for "field" data types

While not "file-formats", in some workflows, particularly when interacting with a data
store such as in Arcana, it is useful to interchangeably interact with file and field
data, so the classes in this module are provided to support these use cases.
"""
import decimal
import typing as ty
import attrs
from fileformats.core import Field
from fileformats.core.mixin import WithClassifiers
from fileformats.core.exceptions import FormatMismatchError


class Singular(Field):
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
        raise FormatMismatchError(str(e)) from None


def integer_converter(value):
    if isinstance(value, float):
        raise FormatMismatchError(
            f"Cannot convert float ({value}) to integer field without potential loss "
            "of information"
        )
    try:
        return int(value)
    except ValueError as e:
        raise FormatMismatchError(str(e)) from None


def decimal_converter(value):
    if isinstance(value, Decimal):
        return value.value
    try:
        return decimal.Decimal(value)
    except decimal.InvalidOperation as e:
        raise FormatMismatchError(str(e)) from None


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
            raise FormatMismatchError(str(e)) from None
    return value


def array_converter(value):
    if isinstance(value, str):
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1]
        elif value.startswith("[") or value.endswith("]"):
            raise FormatMismatchError(f"Unmatched brackets in array field {value}")
        value = tuple(v.strip() for v in value.split(","))
    else:
        try:
            value = tuple(value)
        except ValueError as e:
            raise FormatMismatchError(str(e)) from None
    return value


@attrs.define(repr=False)
class Text(Singular):

    value: str = attrs.field(converter=text_converter)

    primitive = str

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return f'{self._type_name}("{self.value}")'


@attrs.define(repr=False)
class Integer(Singular, ScalarMixin):

    value: int = attrs.field(converter=integer_converter)

    primitive = int

    def __int__(self):
        return self.value

    def __float__(self):
        return float(self.value)

    def __bool__(self):
        return bool(self.value)

    def __hash__(self):
        return hash(self.value)


@attrs.define(repr=False)
class Decimal(Singular, ScalarMixin):

    value: decimal.Decimal = attrs.field(converter=decimal_converter)

    primitive = float

    def __float__(self):
        return float(self.value)

    def __bool__(self):
        return bool(self.value)

    def __hash__(self):
        return hash(self.value)


@attrs.define(repr=False)
class Boolean(Singular, LogicalMixin):

    primitive = bool

    value: bool = attrs.field(converter=boolean_converter)

    def __str__(self):
        return str(self.value).lower()

    def __bool__(self):
        return self.value

    def __hash__(self):
        return hash(self.value)


@attrs.define(auto_attribs=False, repr=False)
class Array(WithClassifiers, Field):

    # WithClassifiers class attrs
    classifiers_attr_name: str = "item_type"
    multiple_classifiers: bool = False
    allowed_classifiers: ty.Tuple[ty.Type[Singular]] = (Singular,)
    item_type: ty.Union[ty.Type[Singular], None] = None

    primitive = tuple

    value: tuple = attrs.field(converter=array_converter)

    def __attrs_post_init__(self):
        # Ensure items are of the correct type
        if self.item_type is not None:
            self.value = tuple(self.item_type(i).value for i in self.value)

    def __str__(self):
        return (
            "["
            + ",".join(
                str(self.item_type(i))
                if self.item_type is not None
                else i  # pylint: disable=not-callable
                for i in self.value
            )
            + "]"
        )

    def __iter__(self):
        return iter(self.value)

    def __hash__(self):
        return hash(self.value)
