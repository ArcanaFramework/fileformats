from fileformats.generic import FileSet
from fileformats.core.utils import from_mime


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
