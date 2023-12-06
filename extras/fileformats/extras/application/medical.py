import typing as ty
from pathlib import Path
from random import Random
import pydicom
from fileformats.core import FileSet
from fileformats.application import Dicom
import medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c


@FileSet.read_metadata.register
def dicom_read_metadata(
    dicom: Dicom, selected_keys: ty.Optional[ty.Sequence[str]] = None
) -> ty.Mapping[str, ty.Any]:
    dcm = pydicom.dcmread(dicom.fspath, specific_tags=selected_keys)
    [getattr(dcm, a, None) for a in dir(dcm)]  # Ensure all keywords are set
    metadata = {
        e.keyword: e.value  # type: ignore[union-attr]
        for e in dcm.elements()
        if getattr(e, "keyword", False) and e.keyword != "PixelData"  # type: ignore[union-attr]
    }
    return metadata


@FileSet.generate_sample_data.register
def dicom_generate_sample_data(
    dicom: Dicom,
    dest_dir: Path,
    seed: ty.Union[int, Random] = 0,
    stem: ty.Optional[str] = None,
) -> ty.Iterable[Path]:
    return next(
        medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c.get_image().iterdir()
    )
