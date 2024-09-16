from fileformats.generic import BinaryFile
from fileformats.core.mixin import WithMagicNumber


class Dicom(WithMagicNumber, BinaryFile):

    iana_mime = "application/dicom"
    magic_number = b"DICM"
    magic_number_offset = 128
    binary = True

    alternate_exts = (".dcm",)  # dcm is recommended not required
