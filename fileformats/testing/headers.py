from fileformats.generic import UnicodeFile, BinaryFile
from fileformats.application import Json
from fileformats.core.mixin import WithSideCars, WithSeparateHeader, WithMagicNumber


class YFile(UnicodeFile):
    ext = ".y"


class ZFile(UnicodeFile):
    ext = ".z"


class Xyz(WithSideCars, UnicodeFile):

    ext = ".x"
    side_car_types = (YFile, ZFile)


class MyFormat(UnicodeFile):

    ext = ".my"


class MyFormatGz(MyFormat):

    ext = ".my.gz"


class MyFormatX(WithSideCars, MyFormat):

    side_car_types = (Json,)


class MyBinaryFormat(WithMagicNumber, UnicodeFile):
    ext = ".my"
    magic_number = b"MYFORMAT"


class MyHeader(UnicodeFile):
    ext = ".myhdr"


class MyBinaryFormatX(WithSeparateHeader, MyFormat):
    header_type = MyHeader


class MyOtherBinaryFormatX(WithMagicNumber, WithSeparateHeader, BinaryFile):
    magic_number = b"MYFORMAT"
    ext = ".my"
    header_type = MyHeader


class YourFormat(UnicodeFile):

    ext = ".yr"


class SeparateHeader(UnicodeFile):

    ext = ".hdr"


class ImageWithHeader(WithSeparateHeader, UnicodeFile):

    ext = ".img"
    header_type = SeparateHeader


class MyFormatGzX(MyFormatX, MyFormatGz):

    pass


class EncodedText(UnicodeFile):
    """A text file where the characters ASCII codes are shifted on conversion
    from text
    """

    ext = ".enc"
    binary = False
