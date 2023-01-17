from ._version import __version__
from fileformats.core.generic import File
from fileformats.core.mixin import WithMagic


# General image formats
class Image(File):
    pass


class Gif(Image, WithMagic):
    ext = ".gif"
    iana = "image/gif"
    magic = 0x47494638


class Png(Image, WithMagic):
    ext = ".png"
    iana = "image/png"
    magic = 0x89504E47


class Jpeg(Image):
    ext = (".jpg", ".jpeg")
    iana = "image/jpeg"
