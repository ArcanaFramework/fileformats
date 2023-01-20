from ..core import __version__
from fileformats.generic import File
from fileformats.archive import Zip
from fileformats.core.mixin import WithMagicNumber


# Document formats
class Document(File):
    iana_mime = None


class Pdf(Document, WithMagicNumber):
    ext = ".pdf"
    magic_number = b"%PDF-"
    binary = True

    iana_mime = "application/pdf"


class Msword(Document):
    ext = ".doc"
    binary = True

    iana_mime = "application/msword"


class MswordX(Zip, Document):
    ext = ".docx"

    iana_mime = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
