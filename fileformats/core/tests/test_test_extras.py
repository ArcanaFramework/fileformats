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
        expected_root = Path(Path().cwd().drive)
    else:
        expected_root = Path("/")
    assert mock.fspath == expected_root / "mock" / "foo.foo"
    assert not mock.fspath.exists()
    assert isinstance(mock, MockMixin)
