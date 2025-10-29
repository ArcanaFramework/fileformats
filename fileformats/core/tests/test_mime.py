from fileformats.application import Cdfx___Xml
from fileformats.core.identification import from_mime
from fileformats.generic import DirectoryOf, FileSet
from fileformats.testing import Classified, U, V
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


def test_vendor_to_mime_roundtrip() -> None:
    assert Psi.mime_like == "testing/vnd.testing.psi"
    assert from_mime("testing/vnd.testing.psi") is Psi


def test_vendor_to_mime_classified_rountrip() -> None:
    assert (
        VendorClassified[Zeta, Theta].mime_like
        == "testing/[vnd.testing.theta..vnd.testing.zeta]+vnd.testing.vendor-classified"
    )
    assert (
        from_mime(
            "testing/[vnd.testing.theta..vnd.testing.zeta]+vnd.testing.vendor-classified"
        )
        is VendorClassified[Zeta, Theta]
    )


def test_vendor_to_mime_parent_classified_rountrip() -> None:
    assert (
        Classified[Zeta, Theta].mime_like
        == "testing/[vnd.testing.theta..vnd.testing.zeta]+classified"
    )
    assert (
        from_mime("testing/[vnd.testing.theta..vnd.testing.zeta]+classified")
        is Classified[Zeta, Theta]
    )


def test_vendor_to_mime_parent_classifiers_rountrip() -> None:
    assert (
        VendorClassified[U, V].mime_like
        == "testing/[u..v]+vnd.testing.vendor-classified"
    )
    assert (
        from_mime("testing/[u..v]+vnd.testing.vendor-classified")
        is VendorClassified[U, V]
    )


def test_vendor_roundtrip() -> None:

    mime = Wordprocessingml_Document.mime_like
    assert Wordprocessingml_Document is from_mime(mime)


def test_vendor_in_container_roundtrip() -> None:

    mime = DirectoryOf[Wordprocessingml_Document].mime_like
    assert DirectoryOf[Wordprocessingml_Document] is from_mime(mime)


def test_native_container_roundtrip() -> None:

    mime = Cdfx___Xml.mime_like
    assert Cdfx___Xml is from_mime(mime)
