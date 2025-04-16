import tempfile
import attrs
from pathlib import Path
import pytest
from pydra.compose import python, shell
from fileformats.generic import File
from fileformats.testing import Foo, Bar, Baz, Qux
from fileformats.core import converter
from fileformats.core.exceptions import FormatConversionError
from conftest import write_test_file


@pytest.fixture
def FooBarConverter():
    work_dir = Path(tempfile.mkdtemp())

    @converter
    @python.define(outputs={"out_file": Bar})  # type: ignore[misc]
    def FooBarConverter_(in_file: Foo):
        return Bar(write_test_file(work_dir / "bar.bar", in_file.raw_contents))

    return FooBarConverter_


@pytest.fixture
def BazBarConverter():
    work_dir = Path(tempfile.mkdtemp())

    @converter(out_file="out")
    @python.define(outputs={"out": Bar})  # type: ignore[misc]
    def BazBarConverter_(in_file: Baz):
        assert in_file
        return Bar(write_test_file(work_dir / "bar.bar", in_file.raw_contents))

    return BazBarConverter_


@pytest.fixture
def FooQuxConverter():
    @converter(source_format=Foo, target_format=Qux)
    @shell.define
    class FooQuxConverter_(shell.Task["FooQuxConverter_.Outputs"]):

        in_file: File = shell.arg(help="the input file", argstr="")
        executable = "cp"

        class Outputs(shell.Outputs):
            out_file: File = shell.outarg(
                help="output file",
                argstr="",
                position=-1,
                path_template="out.qux",
            )

    return FooQuxConverter_


def test_get_converter_functask(FooBarConverter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    assert attrs.asdict(Bar.get_converter(Foo).task) == attrs.asdict(FooBarConverter())


def test_get_converter_shellcmd(FooQuxConverter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    assert attrs.asdict(Qux.get_converter(Foo).task) == attrs.asdict(FooQuxConverter())


def test_get_converter_fail(work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    with pytest.raises(FormatConversionError):
        Baz.get_converter(Foo)


def test_convert_functask(FooBarConverter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    foo = Foo(fspath)
    bar = Bar.convert(foo)
    assert type(bar) is Bar
    assert bar.raw_contents == foo.raw_contents


def test_convert_shellcmd(FooQuxConverter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    foo = Foo(fspath)
    qux = Qux.convert(foo)
    assert type(qux) is Qux
    assert qux.raw_contents == foo.raw_contents


def test_convert_mapped_conversion(BazBarConverter, work_dir):

    fspath = work_dir / "test.baz"
    write_test_file(fspath)
    baz = Baz(fspath)
    bar = Bar.convert(baz)
    assert type(bar) is Bar
    assert bar.raw_contents == baz.raw_contents
