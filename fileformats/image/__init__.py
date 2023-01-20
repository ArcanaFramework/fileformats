from ..core import __version__
from fileformats.generic import File
from fileformats.core.mixin import WithMagicNumber
from fileformats.core import mark
from fileformats.core.exceptions import FormatMismatchError


# General image formats
class Image(File):
    iana_mime = None


class RasterImage(Image):
    iana_mime = None


class VectorImage(Image):
    iana_mime = None


class Bmp(RasterImage, WithMagicNumber):
    ext = ".bmp"
    magic_number = b"BM"
    iana_mime = "image/bmp"


class Gif(RasterImage, WithMagicNumber):
    ext = ".gif"
    iana_mime = "image/gif"
    magic_number = b"GIF8"


class Png(RasterImage, WithMagicNumber):
    ext = ".png"
    iana_mime = "image/png"
    magic_number = b".PNG"


class Jpeg(RasterImage, WithMagicNumber):
    ext = ".jpg"
    alternate_exts = (".jpeg", ".jpe", ".jfif", ".jif")
    iana_mime = "image/jpeg"
    magic_number = "ffd8ffe0"


class Postscript(RasterImage, WithMagicNumber):
    ext = ".eps"
    alternate_exts = (".ps",)
    magic_number = b"%!"
    iana_mime = "application/postscript"


class Svg_Xml(VectorImage):
    ext = ".svg"
    iana_mime = "image/svg+xml"


class Tiff(RasterImage):

    ext = ".tiff"
    iana_mime = "image/tiff"

    magic_number_le = "49492A00"
    magic_number_be = "4D4D002A"

    @mark.check
    def endianness(self):
        read_magic = self.read_contents(len(self.magic_number_le))
        if read_magic == bytes.fromhex(self.magic_number_le):
            endianness = "little"
        elif read_magic == bytes.fromhex(self.magic_number_be):
            endianness = "big"
        else:
            read_magic_str = bytes.hex(read_magic)
            raise FormatMismatchError(
                f"Magic number of file '{read_magic_str}' doesn't match either the "
                f"little-endian '{self.magic_number_le}' and big-endian "
                f"'{self.magic_number_be}'"
            )
        return endianness
