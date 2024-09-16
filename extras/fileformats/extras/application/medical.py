import typing as ty
from pathlib import Path
import pydicom
from fileformats.core import FileSet, extra_implementation
from fileformats.application import Dicom
import medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c
from fileformats.core import SampleFileGenerator


@extra_implementation(FileSet.read_metadata)
def dicom_read_metadata(
    dicom: Dicom,
    specific_tags: ty.Optional[ty.Collection[str]] = None,
    **kwargs: ty.Any,
) -> ty.Mapping[str, ty.Any]:
    dcm = pydicom.dcmread(
        dicom.fspath,
        specific_tags=list(specific_tags if specific_tags is not None else []),
    )
    [getattr(dcm, a, None) for a in dir(dcm)]  # Ensure all keywords are set
    metadata = {
        e.keyword: e.value
        for e in dcm.elements()
        if isinstance(e, pydicom.DataElement)
        and getattr(e, "keyword", False)
        and e.keyword != "PixelData"
    }
    return metadata


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
