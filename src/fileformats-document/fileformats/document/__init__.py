from ._version import __version__
from fileformats.core import File
from fileformats.archive import Zip
from fileformats.core.mixin import WithMagic


# Document formats
class Document(File):
    iana = None


class Pdf(Document, WithMagic):
    ext = ".pdf"
    magic = b"%PDF-"
    binary = True

    iana = "application/pdf"


class Msword(Document):
    ext = ".doc"
    binary = True

    iana = "application/msword"


class MswordX(Zip, Document):
    ext = ".docx"

    iana = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
