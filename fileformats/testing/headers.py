from fileformats.generic import File
from fileformats.serialization import Json
from fileformats.core.mixin import WithSideCars, WithSeparateHeader


class Y(File):
    ext = ".y"


class Z(File):
    ext = ".z"


class Xyz(WithSideCars, File):

    ext = ".x"
    side_car_types = (Y, Z)


class MyFormat(File):

    ext = ".my"


class MyFormatGz(MyFormat):

    ext = ".my.gz"


class MyFormatX(WithSideCars, MyFormat):

    side_car_types = (Json,)


class YourFormat(File):

    ext = ".yr"


class SeparateHeader(File):

    ext = ".hdr"


class ImageWithHeader(WithSeparateHeader, File):

    ext = ".img"
    header_type = SeparateHeader


class MyFormatGzX(MyFormatX, MyFormatGz):

    pass


class EncodedText(File):
    """A text file where the characters ASCII codes are shifted on conversion
    from text
    """

    ext = ".enc"
