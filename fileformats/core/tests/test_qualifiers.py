from __future__ import annotations
import pytest
import pydra.mark
from fileformats.core import from_mime, DataType, FileSet
from fileformats.core.mark import converter
from fileformats.archive import Zip
from fileformats.generic import DirectoryContaining
from fileformats.field import Array, Integer, Decimal, Text, Boolean
from fileformats.core.exceptions import (
    FileFormatsError,
    FormatConversionError,
    FormatRecognitionError,
    FormatMismatchError,
)
from fileformats.testing import (
    A,
    B,
    C,
    D,
    E,
    F,
    G,
    H,
    J,
    K,
    L,
    M,
    N,
    P,
    Q,
    R,
    TestField,
)


SpecificDataType = DataType.type_var("SpecificDataType")
SpecificFileSet = FileSet.type_var("SpecificFileSet")


def test_qualified_equivalence():

    assert F is F
    assert F[A] is F[A]
    assert F[A, B] is F[B, A]
    assert K[A, B] is not K[B, A]  # ordered qualifers
    assert F[A] is not F[B]
    assert F[SpecificDataType] is F[SpecificDataType]
    assert F[SpecificDataType] is not F[A]
    assert F[SpecificDataType] is not F[SpecificFileSet]


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
    assert FileSet.is_subtype_of(DataType)
    assert SpecificFileSet.is_subtype_of(SpecificDataType)
    assert F[SpecificFileSet].is_subtype_of(F[SpecificDataType])
    assert L[A, E].is_subtype_of(L[A, C])
    assert not L[E, A].is_subtype_of(L[A, C])
    assert K[A, E, B].is_subtype_of(K[A, C, B])
    assert N[J, K].is_subtype_of(N[J, H])  # J is subclass of H,


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
        Q[A]
    assert (
        "Default value for qualifiers attribute 'new_qualifiers_attr' needs to be set"
        in str(e)
    )

    with pytest.raises(FileFormatsError) as e:
        M[A, B]
    assert "Multiple qualifiers not permitted for " in str(e)


# (source_format=F, target_format=H)


@converter
@converter(source_format=F[A], target_format=H[A])  # Additional converter
@pydra.mark.task
def f2h(in_file: F) -> H:
    return in_file


def test_qualifier_converters():

    H.get_converter(F)
    assert F.get_converter(G) is None  # G is subtype of F
    with pytest.raises(FormatConversionError):  # Cannot convert to more specific type
        G.get_converter(F)
    H[A].get_converter(F[A])
    with pytest.raises(FormatConversionError):
        H[B].get_converter(F[B])
    assert F[A].get_converter(G[A]) is None
    assert F.get_converter(G[A]) is None
    with pytest.raises(FormatConversionError):
        F[A].get_converter(F[E])
    with pytest.raises(FormatConversionError):
        F[A].get_converter(G)


@converter(source_format=K[A, B], target_format=L[A, B])
@converter(source_format=K[C, D], target_format=L[D, C])
@converter(source_format=K[A, B, C], target_format=L[A, B])
@converter(source_format=K[A, C, B], target_format=L[C, A])
@pydra.mark.task
def k2l(in_file: K) -> L:
    return in_file


def test_ordered_qualifier_converters():
    L[A, B].get_converter(K[A, B])
    with pytest.raises(FormatConversionError):
        L[B, A].get_converter(K[A, B])
    L[D, C].get_converter(K[C, D])
    with pytest.raises(FormatConversionError):
        L[C, D].get_converter(K[C, D])

    L[C, A].get_converter(K[A, C, B])
    L[C, A].get_converter(K[A, E, B])  # E is a subtype of C


def test_mime_rountrips():

    assert DirectoryContaining[F].mime_like == "testing/f+directory-containing"
    assert from_mime("testing/f+directory-containing") is DirectoryContaining[F]

    # Directory is unordered so sort qualifiers to create unique mime
    assert DirectoryContaining[H, F].mime_like == "testing/f.h+directory-containing"
    assert from_mime("testing/f.h+directory-containing") is DirectoryContaining[F, H]

    # K is ordered
    assert K[B, A].mime_like == "testing/b.a+k"
    assert from_mime("testing/b.a+k") is K[B, A]
    assert from_mime("testing/b.a+k") is not K[A, B]

    with pytest.raises(FormatRecognitionError) as e:
        Array[TestField].mime_like
    assert "Cannot create reversible MIME type for " in str(e)


def test_inherited_qualifiers():

    assert Zip[G].mime_like == "testing/g+zip"
    assert from_mime("testing/g+zip") is Zip[G]


def test_arrays():

    Array[Integer]([1, 2, 3, 4])
    with pytest.raises(FormatMismatchError) as e:
        Array[Integer]([1.5, 2.2])
    assert "Cannot convert float (1.5) to integer field" in str(e)

    assert list(Array[Decimal]([1.5, 2.2])) == [1.5, 2.2]
    assert list(Array[Decimal](["1.5", "2.2"])) == [1.5, 2.2]
    assert list(Array[Decimal]("1.5, 2.2")) == [1.5, 2.2]
    assert list(Array[Decimal]("[1.5, 2.2]")) == [1.5, 2.2]
    assert list(Array[Text]("[1.5, 2.2]")) == ["1.5", "2.2"]

    assert list(Array[Boolean]("yes, YES, no, 0, 1, False, True, true")) == [
        True,
        True,
        False,
        False,
        True,
        False,
        True,
        True,
    ]

    assert list(from_mime("field/integer+array")("1,2,3,4,5")) == [1, 2, 3, 4, 5]


# Template-from-template conversions


@converter
@pydra.mark.task
def f2n_template(in_file: F[SpecificDataType]) -> N[SpecificDataType]:
    return in_file


@converter
@pydra.mark.task
def f2p_template(in_file: F[SpecificDataType]) -> P[SpecificDataType]:
    return in_file


@converter
@pydra.mark.task
def p2n_template(in_file: P[SpecificDataType]) -> N[SpecificDataType]:
    return in_file


def test_wildcard_template_from_template_conversion():
    H[A].get_converter(F[A])
    with pytest.raises(FormatConversionError):
        H[B].get_converter(F[A])


# Template from generic type to template


@converter
@pydra.mark.task
def generic2f(in_file: SpecificDataType) -> F[SpecificDataType]:
    return in_file


@converter
@pydra.mark.task
def generic2n(in_file: SpecificDataType) -> N[SpecificDataType, H]:
    return in_file


def test_wildcard_template_from_generic_conversion():

    F[J].get_converter(J)
    with pytest.raises(FormatConversionError):
        F[K].get_converter(J)

    N[J].get_converter(J)
    N[J, H].get_converter(J)
    with pytest.raises(FormatConversionError):
        F[K, H].get_converter(J)
    with pytest.raises(FormatConversionError):
        F[J, K].get_converter(J)


# Generic from template to  type


@converter
@pydra.mark.task
def f2generic(in_file: F[SpecificDataType]) -> SpecificDataType:
    return in_file


@converter
@pydra.mark.task
def n2generic(in_file: N[SpecificDataType, G]) -> SpecificDataType:
    return in_file


def test_wildcard_generic_from_template_conversion():
    J.get_converter(F[J])
    with pytest.raises(FormatConversionError):
        J.get_converter(F[K])


def test_wildcard_generic_from_multi_template_conversion():

    J.get_converter(N[J, G])
    with pytest.raises(FormatConversionError):
        J.get_converter(N[J, K])


@converter
@pydra.mark.task
def l2r(in_file: L[A, SpecificDataType, C]) -> R[A, SpecificDataType, C, D]:
    return in_file


def test_wildcard_ordered_qualifier_converters():
    R[A, B, C, D].get_converter(L[A, B, C])
    with pytest.raises(FormatConversionError):
        R[A, E, C, D].get_converter(L[A, B, C])
