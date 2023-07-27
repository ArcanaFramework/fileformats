import typing as ty
from pathlib import Path
from fileformats.core.fileset import FileSet, MockMixin
from fileformats.testing import Foo


@FileSet.generate_sample_data.register
def generate_foo_data(file: Foo, dest_dir: Path) -> ty.List[Path]:
    foo_fspath = dest_dir / "test.foo"
    foo_fspath.write_text("foo")
    return [foo_fspath]


def test_sample():
    test_inst = Foo.sample()
    assert test_inst.fspath.exists()
    assert test_inst.fspath.name == "test.foo"


def test_mock():
    mock = Foo.mock()
    assert mock.fspath == Path("/mock/foo.foo")
    assert not mock.fspath.exists()
    assert isinstance(mock, MockMixin)
