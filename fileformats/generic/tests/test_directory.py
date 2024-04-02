from fileformats.generic import Directory, DirectoryContaining, SetOf
from fileformats.testing import MyFormatGz


def test_sample_directory():
    assert isinstance(Directory.sample(), Directory)


def test_sample_directory_containing():
    sample = DirectoryContaining[MyFormatGz].sample()
    assert isinstance(sample, DirectoryContaining[MyFormatGz])
    assert all(isinstance(c, MyFormatGz) for c in sample.contents)


def test_sample_set_of():
    sample = SetOf[MyFormatGz].sample()
    assert isinstance(sample, SetOf)
    assert all(isinstance(c, MyFormatGz) for c in sample.contents)
