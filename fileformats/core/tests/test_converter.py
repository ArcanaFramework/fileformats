import pytest
from fileformats.core.generic import File
from fileformats.core import mark
from fileformats.core.exceptions import FormatConversionError
from conftest import write_test_file

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
def Baz():
    class Baz_(File):

        ext = ".baz"

    return Baz_


@pytest.fixture
def Qux():
    class Qux_(File):

        ext = ".qux"

    return Qux_


@pytest.fixture
def foo_bar_converter(Foo, Bar, work_dir):
    @mark.converter
    @pydra.mark.task
    @pydra.mark.annotate({"return": {"out_file": Bar}})
    def foo_bar_converter_(in_file: Foo):
        return write_test_file(work_dir / "bar.bar", in_file.contents)

    return foo_bar_converter_


@pytest.fixture
def FooQuxConverter(Foo, Qux, work_dir):
    from pydra.engine import specs
    from pydra import ShellCommandTask

    input_fields = [
        (
            "in_file",
            specs.File,
            {
                "help_string": "the input file",
                "argstr": "",
            },
        ),
        (
            "out_file",
            str,
            {
                "help_string": "output file name",
                "argstr": "",
                "position": -1,
                "output_file_template": "out.qux",
            },
        ),
    ]

    FooQux_input_spec = specs.SpecInfo(
        name="Input", fields=input_fields, bases=(specs.ShellSpec,)
    )

    output_fields = [
        (
            "out_file",
            specs.File,
            {
                "help_string": "output file",
            },
        ),
    ]
    FooQux_output_spec = specs.SpecInfo(
        name="Output", fields=output_fields, bases=(specs.ShellOutSpec,)
    )

    @mark.converter(source_format=Foo, target_format=Qux)
    class FooQuxConverter_(ShellCommandTask):

        input_spec = FooQux_input_spec
        output_spec = FooQux_output_spec
        executable = "cp"

    return FooQuxConverter_


@pytest.mark.skipif(pydra is None, reason="Pydra could not be imported")
def test_find_converter_functask(Foo, Bar, foo_bar_converter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    assert Bar.find_converter(Foo) == foo_bar_converter


@pytest.mark.skipif(pydra is None, reason="Pydra could not be imported")
def test_find_converter_shellcmd(Foo, Qux, FooQuxConverter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    assert Qux.find_converter(Foo) == FooQuxConverter


@pytest.mark.skipif(pydra is None, reason="Pydra could not be imported")
def test_find_converter_fail(Foo, Baz, foo_bar_converter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    with pytest.raises(FormatConversionError):
        Baz.find_converter(Foo)


@pytest.mark.skipif(pydra is None, reason="Pydra could not be imported")
def test_convert_functask(Foo, Bar, foo_bar_converter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    foo = Foo(fspath)
    bar = Bar.convert(foo)
    assert type(bar) is Bar
    assert bar.contents == foo.contents


@pytest.mark.skipif(pydra is None, reason="Pydra could not be imported")
def test_convert_shellcmd(Foo, Qux, FooQuxConverter, work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    foo = Foo(fspath)
    qux = Qux.convert(foo)
    assert type(qux) is Qux
    assert qux.contents == foo.contents
