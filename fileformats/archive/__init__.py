from ..core import __version__, import_converters
from warnings import warn
from fileformats.generic import File
from fileformats.core.mixin import WithMagicNumber


class Archive(File):
    "Base class for compressed archives"
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


class Tar_Gzip(Gzip, Tar):
    ext = ".tar.gz"
    alternate_exts = (".tgz",)
    magic_number_offset = 0
    iana_mime = "application/x-tar+gzip"


class ExtractedFile(File):
    """An extracted generic file, used as a target for unzip converters"""

    iana_mime = None


import_converters(__name__)
