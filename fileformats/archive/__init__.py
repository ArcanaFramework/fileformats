from fileformats.core import File


class CompressedArchive(File):
    "Base class for compressed archives"


# Compressed formats
class Zip(CompressedArchive):
    ext = ".zip"


class Gzip(CompressedArchive):
    ext = ".gz"


class Tar(CompressedArchive):
    ext = ".tar"


class Tar_Gzip(Tar, Gzip):
    ext = ".tar.gz"
