from fileformats.core import from_mime
from fileformats.field import Text, Integer, Decimal, Boolean, Array


def test_field_text_mime():
    assert Text.mime_like == "field/text"
    assert from_mime("field/text") is Text


def test_field_integer_mime():
    assert Integer.mime_like == "field/integer"
    assert from_mime("field/integer") is Integer


def test_field_decimal_mime():
    assert Decimal.mime_like == "field/decimal"
    assert from_mime("field/decimal") is Decimal


def test_field_boolean_mime():
    assert Boolean.mime_like == "field/boolean"
    assert from_mime("field/boolean") is Boolean


def test_field_array_mime():
    assert Array.mime_like == "field/array"
    assert from_mime("field/array") is Array
