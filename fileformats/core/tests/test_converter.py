import tempfile
import attrs
from pathlib import Path
import pytest
from pydra.engine.specs import File
from fileformats.testing import Foo, Bar, Baz, Qux
from fileformats.core import mark
from fileformats.core.exceptions import FormatConversionError
from conftest import write_test_file

try:
    import pydra.mark
except ImportError:
    pydra = None


@pytest.fixture(scope="session")
def foo_bar_converter():
    work_dir = Path(tempfile.mkdtemp())

    @mark.converter
    @pydra.mark.task
    @pydra.mark.annotate({"return": {"out_file": Bar}})
    def foo_bar_converter_(in_file: Foo):
        return Bar(write_test_file(work_dir / "bar.bar", in_file.contents))

    return foo_bar_converter_


@pytest.fixture(scope="session")
def baz_bar_converter():
    work_dir = Path(tempfile.mkdtemp())

    @mark.converter(out_file="out")
    @pydra.mark.task
    @pydra.mark.annotate({"return": {"out": Bar}})
    def baz_bar_converter_(in_file: Baz):
        assert in_file
        return Bar(write_test_file(work_dir / "bar.bar", in_file.contents))

    return baz_bar_converter_


@pytest.fixture(scope="session")
def FooQuxConverter():
    from pydra.engine import specs
    from pydra import ShellCommandTask

    input_fields = [
        (
            "in_file",
            File,
            {
                "help_string": "the input file",
                "argstr": "",
            },
        ),
        (
            "out_file",
            Path,
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
            File,
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
