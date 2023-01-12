from fileformats.core import File
from fileformats.core.mixin import WithMagic


# Document formats
class Document(File):
    pass


class Pdf(Document, WithMagic):
    ext = ".pdf"
    magic = b"%PDF-"
    binary = True

    iana = "application/pdf"


class Msword(Document):
    ext = ".doc"
    binary = True

    iana = "application/msword"


class MswordX(Document):

    magic = 0x504B0304
    binary = True

    iana = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
