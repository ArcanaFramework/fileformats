import typing as ty
import attrs
from pathlib import Path
import pytest
from pydra.compose import python, shell
from fileformats.generic import File
from fileformats.testing import Foo, Bar, Baz, Qux
from fileformats.core import converter
from fileformats.core.exceptions import FormatConversionError
from conftest import write_test_file


@converter
@python.define(outputs={"out_file": Bar})  # type: ignore[misc]
def FooBarConverter(in_file: Foo):
    return Bar(write_test_file(Path.cwd() / "bar.bar", in_file.raw_contents))


@converter(out_file="out")
@python.define(outputs={"out": Bar})  # type: ignore[misc]
def BazBarConverter(in_file: Baz):
    assert in_file
    return Bar(write_test_file(Path.cwd() / "bar.bar", in_file.raw_contents))


@converter(source_format=Foo, target_format=Qux)
@shell.define
class FooQuxConverter(shell.Task["FooQuxConverter.Outputs"]):

    in_file: File = shell.arg(help="the input file", argstr="")
    executable = "cp"

    class Outputs(shell.Outputs):
        out_file: File = shell.outarg(
            help="output file",
            argstr="",
            position=-1,
            path_template="out.qux",
        )


def test_get_converter_functask(work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    assert attrs.asdict(Bar.get_converter(Foo).task) == attrs.asdict(FooBarConverter())


def test_get_converter_shellcmd(work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    assert attrs.asdict(Qux.get_converter(Foo).task) == attrs.asdict(FooQuxConverter())


def test_get_converter_fail(work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    with pytest.raises(FormatConversionError):
        Baz.get_converter(Foo)


def test_convert_functask(work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    foo = Foo(fspath)
    bar = Bar.convert(foo)
    assert type(bar) is Bar
    assert bar.raw_contents == foo.raw_contents


def test_convert_shellcmd(work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    foo = Foo(fspath)
    qux = Qux.convert(foo)
    assert type(qux) is Qux
    assert qux.raw_contents == foo.raw_contents


def test_convert_mapped_conversion(work_dir):

    fspath = work_dir / "test.baz"
    write_test_file(fspath)
    baz = Baz(fspath)
    bar = Bar.convert(baz)
    assert type(bar) is Bar
    assert bar.raw_contents == baz.raw_contents


def test_convertible_from():

    assert Bar.convertible_from() == ty.Union[Bar, Foo, Baz]
    assert Qux.convertible_from() == ty.Union[Qux, Foo]
    assert Foo.convertible_from() == Foo
    assert Baz.convertible_from() == Baz
