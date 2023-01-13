from _version import __version__
from fileformats.core import File
from fileformats.core.mixin import WithMagic


class CompressedArchive(File):
    "Base class for compressed archives"
    binary = True


# Compressed formats
class Zip(CompressedArchive, WithMagic):
    ext = ".zip"
    magic = 0x504B0304


class Gzip(CompressedArchive):
    ext = ".gz"


class Tar(CompressedArchive):
    ext = ".tar"


class Tar_Gzip(Tar, Gzip):
    ext = ".tar.gz"
