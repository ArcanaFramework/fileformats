import typing as ty
import pytest
from fileformats.core import DataType
from fileformats.generic import File
from fileformats.core.mixin import WithQualifiers
from fileformats.core.exceptions import FileFormatsError


AnyDataType = ty.TypeVar("AnyDataType")


class FileClassifier(DataType):
    pass


class A(FileClassifier):
    pass


class B(FileClassifier):
    pass


class C(FileClassifier):
    pass


class D(FileClassifier):
    pass


class F(WithQualifiers, File):
    pass


class G(F):
    pass


class H(WithQualifiers, File):

    allowed_qualifier_types = (A, B, C)


class J(H):
    pass


class K(WithQualifiers, File):

    qualifiers_attr_name = "new_contents_type"
    new_content_types = ()
    ordered_qualifiers = True


class L(WithQualifiers, File):

    multiple_qualifiers = False


# @attrs.define
# class J(WithQualifiers, I):
#     qualifiers_attr_name = "new_content_types"
#     new_content_types = ()


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
    assert not J[A].is_subtype_of(J[A, B])
    assert not J[B].is_subtype_of(J[A])
    assert J[A].is_subtype_of(H[A])
    assert J[A, B, C].is_subtype_of(H[A, B])
    assert not J[A].is_subtype_of(H[B])


def test_qualifier_fails():

    H[A, B, C]

    with pytest.raises(FileFormatsError):
        H[D]

    with pytest.raises(FileFormatsError):
        H[A, B, A]

    K[A, B, A]
