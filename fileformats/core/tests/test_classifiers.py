from __future__ import annotations
import decimal
import pytest
import pydra.mark
from fileformats.core import from_mime, DataType, FileSet
from fileformats.core.mark import converter
from fileformats.application import Zip
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
    Classified,
    U,
    V,
    W,
    X,
    # Y,
    Z,
)


SpecificDataType = DataType.type_var("SpecificDataType")
SpecificFileSet = FileSet.type_var("SpecificFileSet")


def test_classified_equivalence():
    assert F is F
    assert F[A] is F[A]
    assert F[A, B] is F[B, A]
    assert K[A, B] is not K[B, A]  # ordered qualifers
    assert F[A] is not F[B]
    assert F[SpecificDataType] is F[SpecificDataType]
    assert F[SpecificDataType] is not F[A]
    assert F[SpecificDataType] is not F[SpecificFileSet]


def test_subtype_testing_1():
    assert issubclass(G, F)


def test_subtype_testing_2():
    assert not issubclass(F, G)


def test_subtype_testing_3():
    assert issubclass(J, J)


def test_subtype_testing_4():
    assert issubclass(J, H)


def test_subtype_testing_5():
    assert issubclass(J[A], J)


def test_subtype_testing_6():
    assert not issubclass(H[A], F)


def test_subtype_testing_7():
    assert not issubclass(H[A], F[A])


def test_subtype_testing_8():
    assert issubclass(J[A, B], J[A])


def test_subtype_testing_9():
    assert not issubclass(J[B], J[A])


def test_subtype_testing_10():
    assert not issubclass(J[A], J[A, B])


def test_subtype_testing_11():
    assert issubclass(J[A], H[A])


def test_subtype_testing_12():
    assert issubclass(J[A, B, C], H[A, B])


def test_subtype_testing_13():
    assert not issubclass(J[A], H[B])


def test_subtype_testing_14():
    assert issubclass(FileSet, DataType)


def test_subtype_testing_15():
    assert issubclass(SpecificFileSet, SpecificDataType)


def test_subtype_testing_15a():
    assert not issubclass(SpecificDataType, SpecificFileSet)


def test_subtype_testing_16():
    assert issubclass(F[SpecificFileSet], F[SpecificDataType])


def test_subtype_testing_16a():
    assert not issubclass(F[SpecificDataType], F[SpecificFileSet])


def test_subtype_testing_17():
    assert issubclass(L[A, E], L[A, C])


def test_subtype_testing_18():
    assert not issubclass(L[E, A], L[A, C])


def test_subtype_testing_19():
    assert issubclass(K[A, E, B], K[A, C, B])


def test_file_classifiers1():
    H[A, B, C]  # A, B, C are all allowable qualifier


def test_file_classifiers2():
    F[D]  # F has no restriction on qualifier types


def test_file_classifiers3():
    with pytest.raises(FileFormatsError, match="Invalid content types provided to"):
        H[D]


def test_file_classifiers4():
    with pytest.raises(
        FileFormatsError, match="Cannot have more than one occurrence of a classifier"
    ):
        H[A, B, A]


def test_file_classifiers5():
    K[A, B, A]  # ordered classifiers allow repeats


def test_file_classifiers6():
    with pytest.raises(
        FileFormatsError,
        match="Default value for classifiers attribute 'new_classifiers_attr' needs to be set",
    ):
        Q[A]


def test_file_classifiers7():
    with pytest.raises(
        FileFormatsError, match="Multiple classifiers not permitted for "
    ):
        M[A, B]


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


def test_mime_roundtrips():
    assert DirectoryContaining[F].mime_like == "testing/f+directory-containing"
    assert from_mime("testing/f+directory-containing") is DirectoryContaining[F]

    # Directory is unordered so sort classifiers to create unique mime
    assert DirectoryContaining[H, F].mime_like == "testing/f.h+directory-containing"
    assert from_mime("testing/f.h+directory-containing") is DirectoryContaining[F, H]

    # K is ordered
    assert K[B, A].mime_like == "testing/b.a+k"
    assert from_mime("testing/b.a+k") is K[B, A]
    assert from_mime("testing/b.a+k") is not K[A, B]

    with pytest.raises(FormatRecognitionError) as e:
        Array[TestField].mime_like
    assert "Cannot create reversible MIME type for " in str(e)


def test_inherited_classifiers():
    assert Zip[G].mime_like == "testing/g+zip"
    assert from_mime("testing/g+zip") is Zip[G]


def test_arrays():
    Array[Integer]([1, 2, 3, 4])
    with pytest.raises(FormatMismatchError) as e:
        Array[Integer]([1.5, 2.2])
    assert "Cannot convert float (1.5) to integer field" in str(e)

    assert list(Array[Decimal](["1.5", "2.2"])) == [
        decimal.Decimal("1.5"),
        decimal.Decimal("2.2"),
    ]
    assert list(Array[Decimal](["1.5", "2.2"])) == [
        decimal.Decimal("1.5"),
        decimal.Decimal("2.2"),
    ]
    assert list(Array[Decimal]("1.5, 2.2")) == [
        decimal.Decimal("1.5"),
        decimal.Decimal("2.2"),
    ]
    assert list(Array[Decimal]("[1.5, 2.2]")) == [
        decimal.Decimal("1.5"),
        decimal.Decimal("2.2"),
    ]
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


def test_wildcard_template_from_generic_conversion1():
    F[J].get_converter(J)


def test_wildcard_template_from_generic_conversion2():
    with pytest.raises(FormatConversionError):
        F[K].get_converter(J)


def test_wildcard_template_from_generic_conversion3():
    N[J].get_converter(J)


def test_wildcard_template_from_generic_conversion4():
    with pytest.raises(FormatConversionError):
        F[K, H].get_converter(J)


def test_wildcard_template_from_generic_conversion5():
    with pytest.raises(FormatConversionError):
        F[J, K].get_converter(J)


def test_wildcard_template_from_generic_conversion6():
    N[K, H].get_converter(K)


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


def test_classifier_categories1():
    Classified[U, X]


def test_classifier_categories2():
    Classified[W, Z]


def test_classifier_categories3():
    with pytest.raises(FileFormatsError, match="Cannot have more than one occurrence"):
        Classified[U, V]


def test_classifier_categories4():
    with pytest.raises(FileFormatsError, match="Cannot have more than one occurrence"):
        Classified[U, W]


def test_classifier_categories5():
    Classified[A, B]


def test_classifier_categories6():
    with pytest.raises(FileFormatsError, match="Cannot have more than one occurrence"):
        Classified[C, E]
