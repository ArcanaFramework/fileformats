import typing as ty
from pathlib import Path
from typing_extensions import TypeAlias
import pydicom.tag
from fileformats.core import FileSet, extra_implementation
from fileformats.application import Dicom
import medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c
from fileformats.core import SampleFileGenerator

TagListType: TypeAlias = ty.Union[
    ty.List[int],
    ty.List[str],
    ty.List[ty.Tuple[int, int]],
    ty.List[pydicom.tag.BaseTag],
]


@extra_implementation(FileSet.read_metadata)
def dicom_read_metadata(
    dicom: Dicom,
    specific_tags: ty.Optional[TagListType] = None,
    **kwargs: ty.Any,
) -> ty.Mapping[str, ty.Any]:
    dcm = pydicom.dcmread(dicom.fspath, specific_tags=specific_tags)
    return Dicom.pydicom_to_dict(dcm)


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
