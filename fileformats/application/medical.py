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

        Returns
        -------
        Dict[str, Any]
            The dictionary representation of the pydicom Dataset
        """
        import pydicom.dataset
        import pydicom.valuerep
        import pydicom.multival
        import pydicom.uid

        # Ensure that all keys are loaded before creating dictionary otherwise the keywords
        # will not be set in the elem
        [getattr(dcm, attr, None) for attr in dir(dcm)]
        dct: ty.Dict[str, ty.Any] = {}
        for elem in dcm.values():
            try:
                key = elem.keyword  # type: ignore[union-attr, attr-defined]
            except AttributeError:
                key = None
            if not key:
                key = elem.tag.json_key  # type: ignore[attr-defined]
            if key not in omit:
                value = elem.value  # type: ignore[attr-defined]
                if isinstance(value, pydicom.multival.MultiValue):
                    value = [str(v) for v in value]
                elif isinstance(value, pydicom.uid.UID):
                    value = str(value)
                elif isinstance(value, bytes):
                    value = value.decode(errors="ignore")
                elif isinstance(value, pydicom.dataset.Dataset):
                    value = cls.pydicom_to_dict(value, omit)
                elif isinstance(value, pydicom.valuerep.IS):
                    value = int(value)
                elif isinstance(value, pydicom.valuerep.DSfloat):
                    value = float(value)
                # Can be handy to be able to access family_name and given_name separately
                # elif isinstance(value, pydicom.valuerep.PersonName):
                #     value = str(value)
                dct[key] = value
        return dct
