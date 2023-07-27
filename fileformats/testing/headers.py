from fileformats.generic import File
from fileformats.serialization import Json
from fileformats.core.mixin import WithSideCars, WithSeparateHeader


class Y(File):
    ext = ".y"
    binary = False


class Z(File):
    ext = ".z"
    binary = False


class Xyz(WithSideCars, File):

    ext = ".x"
    binary = False
    side_car_types = (Y, Z)


class MyFormat(File):

    ext = ".my"
    binary = False


class MyFormatGz(MyFormat):

    ext = ".my.gz"


class MyFormatX(WithSideCars, MyFormat):

    side_car_types = (Json,)


class YourFormat(File):

    ext = ".yr"
    binary = False


class SeparateHeader(File):

    ext = ".hdr"
    binary = False


class ImageWithHeader(WithSeparateHeader, File):

    ext = ".img"
    header_type = SeparateHeader
    binary = False


class MyFormatGzX(MyFormatX, MyFormatGz):

    pass


class EncodedText(File):
    """A text file where the characters ASCII codes are shifted on conversion
    from text
    """

    ext = ".enc"
    binary = False
