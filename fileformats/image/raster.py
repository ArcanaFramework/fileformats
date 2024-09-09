from pathlib import Path
from fileformats.core.typing import Self, TypeAlias
import typing as ty
from fileformats.core.mixin import WithMagicNumber
from fileformats.core import extra
from fileformats.core.exceptions import FormatMismatchError
from .base import Image

# if ty.TYPE_CHECKING:
#     import numpy.typing
#     import numpy as np


DataArrayType: TypeAlias = (
    ty.Any
)  # "numpy.typing.NDArray[ty.Union[np.floating, np.integer]]"


class RasterImage(Image):
    # iana_mime = None
    pass
    binary = True

    @extra
    def read_data(self) -> DataArrayType:
        ...

    @extra
    def write_data(self, data_array: DataArrayType) -> None:
        ...

    @classmethod
    def save_new(cls, fspath: Path, data_array: DataArrayType) -> Self:
        # We have to use a mock object as the data file hasn't been written yet
        mock = cls.mock(fspath)
        mock.write_data(data_array)
        return cls(fspath)


class Bitmap(WithMagicNumber, RasterImage):
    ext = ".bmp"
    magic_number = b"BM"
    iana_mime = "image/bmp"
    alternative_exts = (".dib",)


class Gif(WithMagicNumber, RasterImage):
    ext = ".gif"
    iana_mime = "image/gif"
    magic_number = b"GIF8"


class Png(WithMagicNumber, RasterImage):
    ext = ".png"
    iana_mime = "image/png"
    magic_number = "89504E470D0A1A0A"


class Jpeg(WithMagicNumber, RasterImage):
    ext = ".jpg"
    alternate_exts = (".jpeg", ".jpe", ".jfif", ".jif")
    iana_mime = "image/jpeg"
    magic_number = "ffd8ffe0"


class Tiff(RasterImage):

    ext = ".tiff"
    iana_mime = "image/tiff"

    magic_number_le = "49492A00"
    magic_number_be = "4D4D002A"

    @property
    def endianness(self) -> str:
        read_magic = self.read_contents(len(self.magic_number_le) // 2)
        assert isinstance(read_magic, bytes)
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
