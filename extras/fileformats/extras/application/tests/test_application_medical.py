import pytest
from fileformats.application import Dicom


def test_dicom_metadata():

    dicom = Dicom.sample()

    assert dicom.metadata["EchoTime"] == 2.07


def test_dicom_metadata_with_specific_tags():

    dicom = Dicom(Dicom.sample(), metadata_keys=["EchoTime"])

    assert dicom.metadata["EchoTime"] == 2.07
    with pytest.raises(KeyError):
        dicom.metadata["PatientName"]
