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

T = ty.TypeVar("T")


class Singular(Field[T]):
    pass


class LogicalMixin:
    def __bool__(self) -> bool:
        return bool(self.value)  # type: ignore

    def __and__(self, other: "LogicalMixin") -> bool:
        return self.value and other.value  # type: ignore

    def __or__(self, other: "LogicalMixin") -> bool:
        return self.value or other.value  # type: ignore

    def __not__(self) -> bool:
        return not self.value  # type: ignore

    def __invert__(self) -> bool:
        return not self.value  # type: ignore


class ScalarMixin(LogicalMixin, ty.Generic[T]):
    value: T

    def __add__(self, other: T) -> T:
        return self.value + other  # type: ignore

    def __sub__(self, other: T) -> T:
        return self.value - other  # type: ignore

    def __mul__(self, other: T) -> T:
        return self.value * other  # type: ignore

    def __truediv__(self, other: T) -> T:
        return self.value / other  # type: ignore

    def __floordiv__(self, other: T) -> T:
        return self.value // other  # type: ignore

    def __mod__(self, other: T) -> T:
        return self.value % other  # type: ignore

    def __pow__(self, other: T) -> T:
        return self.value**other  # type: ignore

    def __neg__(self) -> T:
        return -self.value  # type: ignore

    def __pos__(self) -> T:
        return +self.value  # type: ignore

    def __abs__(self) -> T:
        return abs(self.value)  # type: ignore


def text_converter(value: ty.Any) -> str:
    try:
        return str(value)
    except ValueError as e:
        raise FormatMismatchError(str(e)) from None


def integer_converter(value: ty.Any) -> int:
    if isinstance(value, float):
        raise FormatMismatchError(
            f"Cannot convert float ({value}) to integer field without potential loss "
            "of information"
        )
    try:
        return int(value)
    except ValueError as e:
        raise FormatMismatchError(str(e)) from None


def decimal_converter(value: ty.Any) -> decimal.Decimal:
    if isinstance(value, Decimal):
        return value.value
    try:
        return decimal.Decimal(value)
    except decimal.InvalidOperation as e:
        raise FormatMismatchError(str(e)) from None


def boolean_converter(value: ty.Any) -> bool:
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
    assert isinstance(value, bool)
    return value


def array_converter(value: ty.Any) -> ty.Tuple[ty.Any, ...]:
    if isinstance(value, str):
        if (value.startswith("[") and value.endswith("]")) or (
            value.startswith("(") and value.endswith(")")
        ):
            value = value[1:-1]
        elif (
            value.startswith("[")
            or value.endswith("]")
            or value.startswith("(")
            or value.endswith(")")
        ):
            raise FormatMismatchError(f"Unmatched brackets in array field {value}")
        value = tuple(v.strip() for v in value.split(","))
    else:
        try:
            value = tuple(value)
        except ValueError as e:
            raise FormatMismatchError(str(e)) from None
    assert isinstance(value, tuple)
    return value


@attrs.define(repr=False)
class Text(Singular[str]):
    value: str = attrs.field(converter=text_converter)

    primitive = str

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f'{self.type_name}("{self.value}")'


@attrs.define(repr=False)
class Integer(Singular[int], ScalarMixin[int]):
    value: int = attrs.field(converter=integer_converter)

    primitive = int

    def __int__(self) -> int:
        return self.value

    def __float__(self) -> float:
        return float(self.value)

    def __bool__(self) -> bool:
        return bool(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@attrs.define(repr=False)
class Decimal(Singular[decimal.Decimal], ScalarMixin[decimal.Decimal]):
    value: decimal.Decimal = attrs.field(converter=decimal_converter)

    primitive = float  # type: ignore

    def __float__(self) -> float:
        return float(self.value)

    def __bool__(self) -> bool:
        return bool(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


@attrs.define(repr=False)
class Boolean(Singular[bool], LogicalMixin):
    primitive = bool

    value: bool = attrs.field(converter=boolean_converter)

    def __str__(self) -> str:
        return str(self.value).lower()

    def __bool__(self) -> bool:
        return self.value

    def __hash__(self) -> int:
        return hash(self.value)


@attrs.define(auto_attribs=False, repr=False)
class Array(WithClassifiers, Field[tuple], ty.Sequence):
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

    def __str__(self) -> str:
        return (
            "["
            + ",".join(
                (
                    str(self.item_type(i)) if self.item_type is not None else i
                )  # pylint: disable=not-callable
                for i in self.value
            )
            + "]"
        )

    def __iter__(self) -> ty.Iterator[ty.Any]:
        return iter(self.value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __getitem__(self, index) -> ty.Any:
        return self.value[index]
