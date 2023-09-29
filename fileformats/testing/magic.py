from fileformats.generic import File
from fileformats.core.mixin import WithMagicNumber, WithMagicVersion


class Magic(WithMagicNumber, File):

    ext = ".magic"
    binary = True
    magic_number = b"MAGIC"
    magic_offset = 10


class MagicVersion(WithMagicVersion, File):

    ext = ".mag.ver"
    binary = True
    magic_pattern = rb"MAGIC_VERSION{\d\d}\.{\d\d}"
