import typing as ty
from fileformats.generic import BinaryFile
from fileformats.core.mixin import WithMagicNumber

if ty.TYPE_CHECKING:
    import pydicom


class Dicom(WithMagicNumber, BinaryFile):

    iana_mime = "application/dicom"
    magic_number = b"DICM"
    magic_number_offset = 128
    binary = True

    alternate_exts = (".dcm",)  # dcm is recommended not required

    @classmethod
    def pydicom_to_dict(
        cls, dcm: "pydicom.Dataset", omit: ty.Collection[str] = ("PixelData",)
    ) -> ty.Dict[str, ty.Any]:
        """Convert a pydicom Dataset to a dictionary.

        Parameters
        ----------
        dcm : pydicom.Dataset
            The pydicom Dataset to convert.
        omit : Collection[str], optional
            A collection of keys to omit from the dictionary, by default ("PixelData",)
        """
        # Ensure that all keys are loaded before creating dictionary otherwise the keywords
        # will not be set in the elem
        [getattr(dcm, attr, None) for attr in dir(dcm)]
        dct: ty.Dict[str, ty.Any] = {}
        for elem in dcm.values():
            try:
                key = elem.keyword
            except AttributeError:
                key = None
            if not key:
                key = elem.tag.json_key
            if key not in omit:
                dct[key] = elem.value
        return dct
