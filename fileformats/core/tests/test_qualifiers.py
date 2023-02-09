import pytest
import pydra.mark
from fileformats.core.mark import converter
from fileformats.core.exceptions import FileFormatsError, FormatConversionError
from fileformats.testing import A, B, C, D, E, F, G, H, J, K, L, AnyDataType


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

    with pytest.raises(FileFormatsError):
        H[D]  # D is not in list of allowable qualifier types for H

    with pytest.raises(FileFormatsError):
        H[A, B, A]  # unordered qualifiers don't allow repeats

    K[A, B, A]  # ordered qualifiers allow repeats

    with pytest.raises(FileFormatsError):
        L[A]  # Missing default value for "new_qualifiers_type"


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
