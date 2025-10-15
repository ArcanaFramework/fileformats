from fileformats.application import Cdfx___Xml
from fileformats.core.identification import from_mime
from fileformats.generic import DirectoryOf, FileSet
from fileformats.testing import Classified, U, V
from fileformats.testing_subpackage import Psi, SubpackageClassified, Theta, Zeta
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


def test_subpackage_to_mime_roundtrip() -> None:
    assert Psi.mime_like == "testing-subpackage/psi"
    assert from_mime("testing-subpackage/psi") is Psi


def test_subpackage_to_mime_classified_rountrip() -> None:
    assert (
        SubpackageClassified[Zeta, Theta].mime_like
        == "testing-subpackage/theta..zeta+subpackage-classified"
    )
    assert (
        from_mime("testing-subpackage/theta..zeta+subpackage-classified")
        is SubpackageClassified[Zeta, Theta]
    )


def test_subpackage_to_mime_parent_classified_rountrip() -> None:
    assert (
        Classified[Zeta, Theta].mime_like == "testing-subpackage/theta..zeta+classified"
    )
    assert (
        from_mime("testing-subpackage/theta..zeta+classified")
        is Classified[Zeta, Theta]
    )


def test_subpackage_to_mime_parent_classifiers_rountrip() -> None:
    assert (
        SubpackageClassified[U, V].mime_like
        == "testing-subpackage/u..v+subpackage-classified"
    )
    assert (
        from_mime("testing-subpackage/u..v+subpackage-classified")
        is SubpackageClassified[U, V]
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
