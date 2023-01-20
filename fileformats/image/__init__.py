from ..core import __version__
from fileformats.generic import File
from fileformats.core.mixin import WithMagicNumber


# General image formats
class Image(File):
    iana = None


class Bmp(Image, WithMagicNumber):
    ext = ".bmp"
    magic_number = b"BM"
    iana = "image/bmp"


class Gif(Image, WithMagicNumber):
    ext = ".gif"
    iana = "image/gif"
    magic_number = b"GIF8"


class Png(Image, WithMagicNumber):
    ext = ".png"
    iana = "image/png"
    magic_number = b".PNG"


class Jpeg(Image, WithMagicNumber):
    ext = (".jpg", ".jpeg")
    iana = "image/jpeg"
    magic_number = "ffd8ffe0"


class Postscript(Image, WithMagicNumber):
    ext = ".eps"
    alternate_exts = (".ps",)
    magic_number = b"%!"
    iana = "application/postscript"
