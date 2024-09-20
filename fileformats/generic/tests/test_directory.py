from fileformats.generic import Directory, DirectoryOf, SetOf
from fileformats.testing import MyFormatGz


def test_sample_directory():
    assert isinstance(Directory.sample(), Directory)


def test_sample_directory_of():
    sample = DirectoryOf[MyFormatGz].sample()
    assert isinstance(sample, DirectoryOf[MyFormatGz])
    assert all(isinstance(c, MyFormatGz) for c in sample.contents)


def test_sample_set_of():
    sample = SetOf[MyFormatGz].sample()
    assert isinstance(sample, SetOf)
    assert all(isinstance(c, MyFormatGz) for c in sample.contents)
