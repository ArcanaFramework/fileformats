from ..core import __version__
from fileformats.core.generic import File
from fileformats.core.mixin import WithMagic


# General image formats
class Image(File):
    iana = None


class Bmp(Image, WithMagic):
    ext = ".bmp"
    magic = b"BM"
    iana = "image/bmp"


class Gif(Image, WithMagic):
    ext = ".gif"
    iana = "image/gif"
    magic = b"GIF8"


class Png(Image, WithMagic):
    ext = ".png"
    iana = "image/png"
    magic = b".PNG"


class Jpeg(Image, WithMagic):
    ext = (".jpg", ".jpeg")
    iana = "image/jpeg"
    magic = "ffd8ffe0"


class Postscript(Image, WithMagic):
    ext = ".eps"
    alternate_exts = (".ps",)
    magic = b"%!"
    iana = "application/postscript"
