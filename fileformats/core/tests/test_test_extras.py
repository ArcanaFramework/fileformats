from pathlib import Path
from fileformats.core.fileset import MockMixin
from fileformats.testing import Foo


def test_sample():
    test_inst = Foo.sample()
    assert test_inst.fspath.exists()
    assert test_inst.fspath.suffix == ".foo"


def test_mock():
    mock = Foo.mock()
    assert mock.fspath == Path("/mock/foo.foo")
    assert not mock.fspath.exists()
    assert isinstance(mock, MockMixin)
