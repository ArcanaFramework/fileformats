from pathlib import Path
import platform
from fileformats.core.fileset import MockMixin
from fileformats.testing import Foo


def test_sample():
    test_inst = Foo.sample()
    assert test_inst.fspath.exists()
    assert test_inst.fspath.suffix == ".foo"


def test_mock():
    mock = Foo.mock()
    if platform.system() == "Windows":
        expected = Path(f"{Path().cwd().drive}\\mock\\foo.foo")
    else:
        expected = Path("/mock/foo.foo")
    assert mock.fspath == expected
    assert not mock.fspath.exists()
    assert isinstance(mock, MockMixin)
