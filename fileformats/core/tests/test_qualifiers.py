import pytest
import pydra.mark
from fileformats.core import from_mime
from fileformats.core.mark import converter
from fileformats.archive import Zip
from fileformats.generic import Directory
from fileformats.field import Array
from fileformats.core.exceptions import (
    FileFormatsError,
    FormatConversionError,
    FormatRecognitionError,
)
from fileformats.testing import A, B, C, D, E, F, G, H, J, K, L, TestField, AnyDataType


def test_qualified_equivalence():

    assert F is F
    assert F[A] is F[A]
    assert F[A] is not F[B]
    assert F[AnyDataType] is F[AnyDataType]
    assert F[AnyDataType] is not F[A]


def test_subtype_testing():

    assert G.is_subtype_of(F)
    assert not F.is_subtype_of(G)
    assert J.is_subtype_of(J)
    assert J.is_subtype_of(H)
    assert J[A].is_subtype_of(J)
    assert not H[A].is_subtype_of(F)
    assert not H[A].is_subtype_of(F[A])
    assert J[A, B].is_subtype_of(J[A])
    assert not J[B].is_subtype_of(J[A])
    assert not J[A].is_subtype_of(J[A, B])
    assert J[A].is_subtype_of(H[A])
    assert J[A, B, C].is_subtype_of(H[A, B])
    assert not J[A].is_subtype_of(H[B])


def test_qualifier_fails():

    H[A, B, C]  # A, B, C are all allowable qualifier
    F[D]  # F has no restriction on qualifier types

    with pytest.raises(FileFormatsError) as e:
        H[D]
    assert "Invalid content types provided to" in str(e)

    with pytest.raises(FileFormatsError) as e:
        H[A, B, A]
    assert "Cannot have more than one occurrence of a qualifier" in str(e)

    K[A, B, A]  # ordered qualifiers allow repeats

    with pytest.raises(FileFormatsError) as e:
        L[A]
    assert (
        "Default value for qualifiers attribute 'new_qualifiers_attr' needs to be set"
        in str(e)
    )


def test_qualifier_converters():
    @converter
    @converter(source_format=F[A], target_format=H[A])
    @pydra.mark.task
    def f2h(in_file: F) -> H:
        return in_file

    H.get_converter(F)
    assert F.get_converter(G) is None  # G is subtype of F
    with pytest.raises(FormatConversionError):  # Cannot convert to more specific type
        G.get_converter(F)
    H[A].get_converter(F[A])
    assert F[A].get_converter(G[A]) is None
    assert F.get_converter(G[A]) is None
    assert F[A].get_converter(F[E]) is None
    with pytest.raises(FormatConversionError):
        assert F[A].get_converter(G) is None


def test_mime_rountrips():

    assert Directory[F].mime_like == "testing/f+directory"
    assert from_mime("testing/f+directory") is Directory[F]

    with pytest.raises(FormatRecognitionError) as e:
        Array[TestField].mime_like
    assert "Cannot create reversible MIME type for " in str(e)


def test_inherited_qualifiers():

    assert from_mime(Zip[G].mime_like) == Zip[G]
