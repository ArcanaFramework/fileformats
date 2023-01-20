from ..core import __version__
from warnings import warn
from fileformats.generic import File
from fileformats.core.mixin import WithMagicNumber


class Archive(File):
    "Base class for compressed archives"
    binary = True
    iana_mime = None


# Compressed formats
class Zip(Archive, WithMagicNumber):
    ext = ".zip"
    magic_number = "504B0304"
    iana_mime = "application/zip"


class Bzip(Archive, WithMagicNumber):
    ext = ".bzip"
    magic_number = "425a"
    iana_mime = "application/bzip"


class Gzip(Archive, WithMagicNumber):
    ext = ".gz"
    magic_number = "1F8B08"
    iana_mime = "application/gzip"


class Tar(Archive, WithMagicNumber):
    ext = ".tar"
    magic_number = "7573746172"
    magic_number_offset = 257
    iana_mime = "application/x-tar"


class Tar_Gzip(Gzip, Tar):
    ext = ".tar.gz"
    alternate_exts = (".tgz",)
    magic_number_offset = 0
    iana_mime = "application/x-tar+gzip"


try:
    from .converters import *
except ImportError:
    warn(
        f"could not import converters for {__name__}  module, please install "
        "fileformats[converters] if conversion is desired"
    )
