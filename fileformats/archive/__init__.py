from fileformats.core import __version__
from warnings import warn
from fileformats.core import FileSet
from fileformats.core.mixin import WithQualifiers
from fileformats.generic import File
from fileformats.core.mixin import WithMagicNumber


class Archive(WithQualifiers, File):
    "Base class for compressed archives"

    qualifiers_attr_name = "archived_type"
    archived_type = None
    multiple_qualifiers = False
    allowed_qualifiers = (FileSet,)
    generically_qualifies = True

    binary = True
    iana_mime = None


# Compressed formats
class Zip(WithMagicNumber, Archive):
    ext = ".zip"
    magic_number = "504B0304"
    iana_mime = "application/zip"


class Bzip(WithMagicNumber, Archive):
    ext = ".bzip"
    magic_number = "425a"
    iana_mime = "application/bzip"


class Gzip(WithMagicNumber, Archive):
    ext = ".gz"
    magic_number = "1F8B08"
    iana_mime = "application/gzip"


class Tar(WithMagicNumber, Archive):
    ext = ".tar"
    magic_number = "7573746172"
    magic_number_offset = 257
    iana_mime = "application/x-tar"


class TarGzip(WithMagicNumber, Archive):
    # FIXME: Should capture the relationship to Gzip and Tar somehow, but a bit
    # tricky to get it right
    ext = ".tar.gz"
    magic_number = "1F8B08"
    alternate_exts = (".tgz",)
    iana_mime = "application/x-tar+gzip"
