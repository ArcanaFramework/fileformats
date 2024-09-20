import typing as ty
from pathlib import Path
import pydicom.tag
from fileformats.core import FileSet, extra_implementation
from fileformats.application import Dicom
import medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c
from fileformats.core import SampleFileGenerator


@extra_implementation(FileSet.read_metadata)
def dicom_read_metadata(
    dicom: Dicom,
    specific_tags: ty.Optional[pydicom.tag.TagListType] = None,
    **kwargs: ty.Any,
) -> ty.Mapping[str, ty.Any]:
    dcm = pydicom.dcmread(dicom.fspath, specific_tags=specific_tags)
    return pydicom_to_dict(dcm)


@extra_implementation(FileSet.generate_sample_data)
def dicom_generate_sample_data(
    dicom: Dicom,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return next(
        medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c.get_image(
            out_dir=generator.dest_dir
        ).iterdir()
    )


def pydicom_to_dict(
    dcm: pydicom.Dataset, omit: ty.Collection[str] = ("PixelData",)
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
        if isinstance(elem, pydicom.DataElement) and elem.keyword:
            key = elem.keyword
        else:
            key = elem.tag.json_key
        if key not in omit:
            dct[key] = elem.value
    return dct
