import tempfile
import attrs
from pathlib import Path
import pytest
from pydra.design import python, shell
from fileformats.generic import File
from fileformats.testing import Foo, Bar, Baz, Qux
from fileformats.core import converter
from fileformats.core.exceptions import FormatConversionError
from conftest import write_test_file

try:
    import pydra.mark
except ImportError:
    pydra = None


@pytest.fixture(scope="session")
def foo_bar_converter():
    work_dir = Path(tempfile.mkdtemp())

    @converter
    @python.define(outputs={"out_file": Bar})  # type: ignore[misc]
    def foo_bar_converter_(in_file: Foo):
        return Bar(write_test_file(work_dir / "bar.bar", in_file.raw_contents))

    return foo_bar_converter_


@pytest.fixture(scope="session")
def baz_bar_converter():
    work_dir = Path(tempfile.mkdtemp())

    @converter(out_file="out")
    @python.define(outputs={"out": Bar})  # type: ignore[misc]
    def baz_bar_converter_(in_file: Baz):
        assert in_file
        return Bar(write_test_file(work_dir / "bar.bar", in_file.raw_contents))

    return baz_bar_converter_


@pytest.fixture(scope="session")
def FooQuxConverter():
    @converter(source_format=Foo, target_format=Qux)
    @shell.define
    class FooQuxConverter_:

        in_file: File = shell.arg(help="the input file", argstr="")
        executable = "cp"

        class Outputs:
            out_file: File = shell.outarg(
                help="output file",
                argstr="",
                position=-1,
                output_file_template="out.qux",
            )

    return FooQuxConverter_


@pytest.mark.skipif(pydra is None, reason="Pydra could not be imported")
def test_get_converter_functask(foo_bar_converter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    assert attrs.asdict(Bar.get_converter(Foo, name="Foo2Bar").inputs) == attrs.asdict(
        foo_bar_converter(name="Foo2Bar").inputs
    )


@pytest.mark.skipif(pydra is None, reason="Pydra could not be imported")
def test_get_converter_shellcmd(FooQuxConverter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    assert attrs.asdict(Qux.get_converter(Foo, name="Foo2Qux").inputs) == attrs.asdict(
        FooQuxConverter(name="Foo2Qux").inputs
    )


@pytest.mark.skipif(pydra is None, reason="Pydra could not be imported")
def test_get_converter_fail(work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    with pytest.raises(FormatConversionError):
        Baz.get_converter(Foo, name="Foo2Baz")


@pytest.mark.skipif(pydra is None, reason="Pydra could not be imported")
def test_convert_functask(foo_bar_converter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    foo = Foo(fspath)
    bar = Bar.convert(foo)
    assert type(bar) is Bar
    assert bar.contents == foo.contents


@pytest.mark.skipif(pydra is None, reason="Pydra could not be imported")
def test_convert_shellcmd(FooQuxConverter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    foo = Foo(fspath)
    qux = Qux.convert(foo)
    assert type(qux) is Qux
    assert qux.contents == foo.contents


@pytest.mark.skipif(pydra is None, reason="Pydra could not be imported")
def test_convert_mapped_conversion(baz_bar_converter, work_dir):

    fspath = work_dir / "test.baz"
    write_test_file(fspath)
    baz = Baz(fspath)
    bar = Bar.convert(baz)
    assert type(bar) is Bar
    assert bar.contents == baz.contents
