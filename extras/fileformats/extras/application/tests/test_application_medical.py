from fileformats.application import Dicom


def test_dicom_metadata():

    dicom = Dicom.sample()

    assert dicom.metadata["EchoTime"] == "2.07"
