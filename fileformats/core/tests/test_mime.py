from fileformats.generic import FileSet
from fileformats.core.utils import from_mime
from fileformats.testing import Classified, U, V
from fileformats.testing_subpackage import Psi, SubpackageClassified, Zeta, Theta


def test_mime_roundtrip():
    for klass in FileSet.all_formats:
        mimetype = klass.mime_type
        assert isinstance(mimetype, str)
        reloaded = from_mime(mimetype)
        assert reloaded is klass


def test_mimelike_roundtrip():
    for klass in FileSet.all_formats:
        mimetype = klass.mime_like
        assert isinstance(mimetype, str)
        reloaded = from_mime(mimetype)
        assert reloaded is klass


def test_subpackage_to_mime_roundtrip():
    assert Psi.mime_like == "testing-subpackage/psi"
    assert from_mime("testing-subpackage/psi") is Psi


def test_subpackage_to_mime_classified_rountrip():
    assert (
        SubpackageClassified[Zeta, Theta].mime_like
        == "testing-subpackage/theta.zeta+subpackage-classified"
    )
    assert (
        from_mime("testing-subpackage/theta.zeta+subpackage-classified")
        is SubpackageClassified[Zeta, Theta]
    )


def test_subpackage_to_mime_parent_classified_rountrip():
    assert (
        Classified[Zeta, Theta].mime_like == "testing-subpackage/theta.zeta+classified"
    )
    assert (
        from_mime("testing-subpackage/theta.zeta+classified") is Classified[Zeta, Theta]
    )


def test_subpackage_to_mime_parent_classifiers_rountrip():
    assert (
        SubpackageClassified[U, V].mime_like
        == "testing-subpackage/u.v+subpackage-classified"
    )
    assert (
        from_mime("testing-subpackage/u.v+subpackage-classified")
        is SubpackageClassified[U, V]
    )
