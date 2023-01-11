import pytest
from fileformats.core.generic import File
from fileformats.core import mark
from conftest import write_test_file

# from fileformats.core import mark
# from fileformats.core.exceptions import FileFormatsError, FormatMismatchError


try:
    import pydra.mark
except ImportError:
    pydra = None


@pytest.fixture
def Foo():
    class Foo_(File):

        ext = ".foo"

    return Foo_


@pytest.fixture
def Bar():
    class Bar_(File):

        ext = ".bar"

    return Bar_


@pytest.fixture
def foo_bar_converter(Foo, Bar, work_dir):
    @mark.converter
    @pydra.mark.task
    @pydra.mark.annotate({"return": {"out_file": Bar}})
    def foo_bar_converter_(in_file: Foo):
        return write_test_file(work_dir / "bar.bar", in_file.contents)

    return foo_bar_converter_


@pytest.mark.skipIf(pydra is None, "Pydra could not be imported")
def test_find_converter(Foo, Bar, foo_bar_converter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    assert Bar.find_converter(Foo) == foo_bar_converter
