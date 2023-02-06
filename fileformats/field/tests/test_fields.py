import pytest
from fileformats.core.exceptions import FormatMismatchError
from fileformats.field import Text, Integer, Decimal, Boolean, Array


def test_field_text():
    text = Text("a-field")
    assert str(text) == "a-field"


def test_field_integer():
    integer = Integer("10")
    assert str(integer) == "10"
    assert int(integer) == 10
    assert integer + 2 == 12
    assert integer * 2 == 20
    assert integer // 2 == 5
    assert integer / 4 == 2.5
    assert integer % 7 == 3
    assert integer**2 == 100
    assert -integer == -10
    assert abs(-integer) == 10


def test_field_integer_fail():
    with pytest.raises(FormatMismatchError):
        Integer("foo")
    with pytest.raises(FormatMismatchError):
        Integer("1.5")


def test_field_decimal():
    decimal = Decimal("20.2")
    assert str(decimal) == "20.2"
    assert float(decimal) == 20.2


def test_field_decimal_fail():
    with pytest.raises(FormatMismatchError):
        Decimal("foo")


def test_field_boolean():
    assert Boolean("True")
    assert Boolean("true")
    assert Boolean("yes")
    assert Boolean("1")
    assert Boolean("YES")
    assert not Boolean("False")
    assert not Boolean("false")
    assert not Boolean("no")
    assert not Boolean("0")
    assert not Boolean("NO")
    boolean = Boolean(True)
    assert boolean and False is False
    assert boolean or False is True
    assert boolean is not False
    assert ~boolean is False


def test_field_boolean_fail():
    with pytest.raises(FormatMismatchError):
        Boolean("foo")
    with pytest.raises(FormatMismatchError):
        Boolean("1.0")


def test_field_array():
    array = Array("[1,2,3,4,5]")
    assert str(array) == "[1,2,3,4,5]"
    array = Array("[1, 2, 3, 4, 5]")
    assert str(array) == "[1,2,3,4,5]"
    array = Array("1,2,3,4,5")
    assert str(array) == "[1,2,3,4,5]"
    assert list(array) == ["1", "2", "3", "4", "5"]
    array = Array[Integer]("1,2,3,4,5")
    assert str(array) == "[1,2,3,4,5]"
    assert list(array) == [1, 2, 3, 4, 5]


def test_field_array_fail():
    with pytest.raises(FormatMismatchError):
        Boolean("1,2,3]")
    with pytest.raises(FormatMismatchError):
        Boolean("[1,2,3")
