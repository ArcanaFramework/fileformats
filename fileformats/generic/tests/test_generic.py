import pytest
from fileformats.generic import FsObject, File, Directory, DirectoryContaining, SetOf
from fileformats.testing import Magic, Foo, MyFormatGz, MyFormatX


def test_sample_fsobject():
    assert isinstance(FsObject.sample(), FsObject)


def test_sample_file():
    assert isinstance(File.sample(), File)


def test_sample_foo():
    assert isinstance(Foo.sample(), Foo)


def test_sample_myformatx():
    assert isinstance(MyFormatX.sample(), MyFormatX)


def test_sample_magic():
    assert isinstance(Magic.sample(), Magic)


@pytest.mark.xfail(
    reason="generate_sample_data for WithMagicVersion file types is not implemented yet"
)
def test_sample_magic_version():
    assert isinstance(Magic.sample(), Magic)


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
