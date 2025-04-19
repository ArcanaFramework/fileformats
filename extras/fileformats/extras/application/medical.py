import sys
import typing as ty
from pathlib import Path
import pydicom.tag
from fileformats.core import FileSet, extra_implementation
from fileformats.application import Dicom
import medimages4tests.dummy.dicom.mri.t1w.siemens.skyra.syngo_d13c
from fileformats.core import SampleFileGenerator

if sys.version_info <= (3, 11):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

TagListType: TypeAlias = ty.Union[
    ty.List[int],
    ty.List[str],
    ty.List[ty.Tuple[int, int]],
    ty.List[pydicom.tag.BaseTag],
]


@extra_implementation(FileSet.read_metadata)
def dicom_read_metadata(
    dicom: Dicom,
    metadata_keys: ty.Optional[TagListType] = None,
    **kwargs: ty.Any,
) -> ty.Mapping[str, ty.Any]:
    dcm = pydicom.dcmread(
        dicom.fspath, specific_tags=metadata_keys, stop_before_pixels=True
    )
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


@extra_implementation(FileSet.load)
def dicom_load(
    dicom: Dicom,
    specific_tags: ty.Optional[TagListType] = None,
    **kwargs: ty.Any,
) -> pydicom.FileDataset:
    return pydicom.dcmread(dicom.fspath, specific_tags=specific_tags)


@extra_implementation(FileSet.save)
def dicom_save(
    dicom: Dicom,
    data: pydicom.FileDataset,
    write_like_original: bool = False,
    **kwargs: ty.Any,
) -> None:
    pydicom.dcmwrite(dicom.fspath, data, write_like_original=write_like_original)
