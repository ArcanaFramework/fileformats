from fileformats.generic import BinaryFile
from .archive import Zip
from fileformats.core.mixin import WithMagicNumber


# Document formats
class Document(BinaryFile):
    # iana_mime = None
    pass


class Pdf(WithMagicNumber, Document):
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


class Postscript(WithMagicNumber, Document):
    ext = ".eps"
    alternate_exts = (".ps",)
    magic_number = b"%!"
    iana_mime = "application/postscript"
