import typing as ty
import pytest
import sys
from fileformats.application import Cdfx___Xml
from fileformats.core import DataType
from fileformats.core.identification import to_mime, from_mime
from fileformats.generic import DirectoryOf, FileSet
from fileformats.application import Zip
from fileformats.testing import Classified, A, B, U, V, X, MyFormat
from fileformats.vendor.testing.testing import Psi, VendorClassified, Theta, Zeta
from fileformats.vendor.openxmlformats_officedocument.application import (
    Wordprocessingml_Document,
)


def test_mime_roundtrip() -> None:
    for klass in FileSet.all_formats:
        mimetype = klass.mime_type
        assert isinstance(mimetype, str)
        reloaded = from_mime(mimetype)
        assert reloaded is klass


def test_mimelike_roundtrip() -> None:
    for klass in FileSet.all_formats:
        mimetype = klass.mime_like
        assert isinstance(mimetype, str)
        reloaded = from_mime(mimetype)
        assert reloaded is klass


UNION_TYPE = U | V if sys.version_info >= (3, 10) else ty.Union[U, V]


@pytest.mark.xfail(
    reason="Classifier mime-types need to be refactored to match desired new format"
)
@pytest.mark.parametrize(
    ["klass", "expected_mime"],
    [
        [Psi, "testing/vnd.testing.psi"],
        [
            VendorClassified[Zeta, Theta],
            "testing/[vnd.testing.theta..vnd.testing.zeta]+vnd.testing.vendor-classified",
        ],
        [
            Classified[Zeta, Theta],
            "testing/[vnd.testing.theta..vnd.testing.zeta]+classified",
        ],
        [VendorClassified[U, V], "testing/[u..v]+vnd.testing.vendor-classified"],
        [Zip[Classified[U]], "testing/u+classified+zip"],
        [Zip[Classified[U, X]], "testing/[u..v]+classified+zip"],
        [Classified[U, Zip[MyFormat]], "testing/[u..my-format+zip]+classified"],
        [
            Classified[Theta, MyFormat[A, B]],
            "testing/[vnd.testing.theta..[a..b]+my-format]+classified",
        ],
        [
            Wordprocessingml_Document,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ],
        [
            DirectoryOf[Wordprocessingml_Document],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document+directory-of",
        ],
        [Cdfx___Xml, "application/vnd.ms-cdfx+xml"],
        [UNION_TYPE, "testing/u,testing/v"],
    ],
)
def test_compound_mime_roundtrip(klass: ty.Type[DataType], expected_mime: str) -> None:
    assert to_mime(klass, official=False) == expected_mime
    assert from_mime(expected_mime) is klass


# def test_vendor_to_mime_roundtrip() -> None:
#     assert Psi.mime_like == "testing/vnd.testing.psi"
#     assert from_mime("testing/vnd.testing.psi") is Psi


# def test_vendor_to_mime_classified_rountrip() -> None:
#     assert (
#         VendorClassified[Zeta, Theta].mime_like
#         == "testing/[vnd.testing.theta..vnd.testing.zeta]+vnd.testing.vendor-classified"
#     )
#     assert (
#         from_mime(
#             "testing/[vnd.testing.theta..vnd.testing.zeta]+vnd.testing.vendor-classified"
#         )
#         is VendorClassified[Zeta, Theta]
#     )


# def test_vendor_to_mime_parent_classified_rountrip() -> None:
#     assert (
#         Classified[Zeta, Theta].mime_like
#         == "testing/[vnd.testing.theta..vnd.testing.zeta]+classified"
#     )
#     assert (
#         from_mime("testing/[vnd.testing.theta..vnd.testing.zeta]+classified")
#         is Classified[Zeta, Theta]
#     )


# def test_vendor_to_mime_parent_classifiers_rountrip() -> None:
#     assert (
#         VendorClassified[U, V].mime_like
#         == "testing/[u..v]+vnd.testing.vendor-classified"
#     )
#     assert (
#         from_mime("testing/[u..v]+vnd.testing.vendor-classified")
#         is VendorClassified[U, V]
#     )


# def test_double_classified_roundtrip1() -> None:
#     assert Zip[Classified[U]].mime_like == "testing/u+classified+zip"
#     assert from_mime("testing/[[u..v]+classified]+zip") is Zip[Classified[U]]


# def test_double_classified_roundtrip2() -> None:
#     assert Zip[Classified[U, V]].mime_like == "testing/[u..v]+classified+zip"
#     assert from_mime("testing/[[u..v]+classified]+zip") is Zip[Classified[U, V]]


# def test_double_classified_roundtrip2() -> None:
#     assert Zip[Classified[U, V]].mime_like == "testing/[u..v]+classified+zip"
#     assert from_mime("testing/[[u..v]+classified]+zip") is Zip[Classified[U, V]]


# def test_vendor_roundtrip() -> None:

#     mime = Wordprocessingml_Document.mime_like
#     assert Wordprocessingml_Document is from_mime(mime)


# def test_vendor_in_container_roundtrip() -> None:

#     mime = DirectoryOf[Wordprocessingml_Document].mime_like
#     assert DirectoryOf[Wordprocessingml_Document] is from_mime(mime)


# def test_native_container_roundtrip() -> None:

#     mime = Cdfx___Xml.mime_like
#     assert Cdfx___Xml is from_mime(mime)
