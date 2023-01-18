from ..core import __version__
from warnings import warn
from fileformats.core import File
from fileformats.core.mixin import WithMagic


class Archive(File):
    "Base class for compressed archives"
    binary = True
    iana = None


# Compressed formats
class Zip(Archive, WithMagic):
    ext = ".zip"
    magic = "504B0304"
    iana = "application/zip"


class Bzip(Archive, WithMagic):
    ext = ".bzip"
    magic = "425a"
    iana = "application/bzip"


class Gzip(Archive, WithMagic):
    ext = ".gz"
    magic = "1F8B08"
    iana = "application/gzip"


class Tar(Archive, WithMagic):
    ext = ".tar"
    magic = "7573746172"
    magic_offset = 257
    iana = "application/x-tar"


class Tar_Gzip(Gzip, Tar):
    ext = ".tar.gz"
    alternate_exts = (".tgz",)
    magic_offset = 0
    iana = "application/x-tar+gzip"


try:
    from .converters import *
except ImportError:
    warn(f"could not import converters for fileformats.{__name__}  module")
