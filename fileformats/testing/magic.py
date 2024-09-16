from fileformats.generic import BinaryFile
from fileformats.core.mixin import WithMagicNumber, WithMagicVersion


class Magic(WithMagicNumber, BinaryFile):

    ext = ".magic"
    magic_number = b"MAGIC"
    magic_offset = 10


class MagicVersion(WithMagicVersion, BinaryFile):

    ext = ".mag.ver"
    magic_pattern = rb"MAGIC_VERSION{\d\d}\.{\d\d}"
