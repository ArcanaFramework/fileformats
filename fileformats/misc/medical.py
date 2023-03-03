from fileformats.generic import File
from fileformats.core.mixin import WithMagicNumber


class Dicom(WithMagicNumber, File):

    iana_mime = "application/dicom"
    magic_number = b"DICM"
    magic_number_offset = 128
    binary = True

    alternate_exts = (".dcm",)  # dcm is recommended not required
