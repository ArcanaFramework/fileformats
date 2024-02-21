from fileformats.generic import File
from fileformats.application import Json
from fileformats.core.mixin import WithSideCars, WithSeparateHeader, WithMagicNumber


class YFile(File):
    ext = ".y"
    binary = False


class ZFile(File):
    ext = ".z"
    binary = False


class Xyz(WithSideCars, File):

    ext = ".x"
    binary = False
    side_car_types = (YFile, ZFile)


class MyFormat(File):

    ext = ".my"
    binary = False


class MyFormatGz(MyFormat):

    ext = ".my.gz"


class MyFormatX(WithSideCars, MyFormat):

    side_car_types = (Json,)


class MyBinaryFormat(WithMagicNumber, File):
    ext = ".my"
    magic_number = b"MYFORMAT"


class MyHeader(File):
    ext = ".myhdr"


class MyBinaryFormatX(WithSeparateHeader, MyFormat):
    header_type = MyHeader


class MyOtherBinaryFormatX(WithMagicNumber, WithSeparateHeader, File):
    magic_number = b"MYFORMAT"
    ext = ".my"
    header_type = MyHeader


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
