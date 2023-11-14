import typing as ty
from random import Random
from pathlib import Path
import pydicom
from fileformats.core import FileSet
from fileformats.application import Dicom
import medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c


@FileSet.read_metadata.register
def dicom_read_metadata(dicom: Dicom, specific_tags=None) -> ty.Mapping[str, ty.Any]:
    dcm = pydicom.dcmread(dicom.fspath, specific_tags=specific_tags)
    [getattr(dcm, a) for a in dir(dcm)]  # Ensure all keywords are set
    metadata = {
        e.keyword: e.value  # type: ignore[union-attr]
        for e in dcm.elements()
        if getattr(e, "keyword", False) and e.keyword != "PixelData"  # type: ignore[union-attr]
    }
    return metadata


@FileSet.generate_sample_data.register
def dicom_generate_sample_data(
    dicom: Dicom, dest_dir: Path, seed: ty.Union[int, Random], stem: ty.Optional[str]
):
    return next(
        medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c.get_image().iterdir()
    )
