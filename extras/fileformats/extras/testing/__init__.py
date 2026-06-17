from pathlib import Path

from fileformats.extras.core import check_optional_dependency
from pydra.compose import python

from fileformats.core import SampleFileGenerator, converter, extra_implementation
from fileformats.testing import (
    AbstractFile,
    ConvertibleToFile,
    EncodedText,
    Foo,
    MyFormat,
    WithExtra,
)
from fileformats.text import TextFile

dummy_import = None


@converter  # pyright: ignore[reportArgumentType]
@python.define(outputs=["out_file"])  # type: ignore[untyped-decorator]
def ConvertibleToConverter(in_file: AbstractFile) -> ConvertibleToFile:
    return ConvertibleToFile.sample()


@converter  # pyright: ignore[reportArgumentType]
@python.define(outputs=["out_file"])  # type: ignore[untyped-decorator]
def EncodedFromTextConverter(in_file: TextFile, shift: int = 1) -> EncodedText:
    contents = in_file.read_text()
    # Encode by shifting ASCII codes forward by 1
    encoded_contents = "".join(chr(ord(c) + shift) for c in contents)
    out_file = EncodedText.sample()
    out_file.write_text(encoded_contents)
    return out_file


@converter  # pyright: ignore[reportArgumentType]
@python.define(outputs=["out_file"])  # type: ignore[untyped-decorator]
def EncodedToTextConverter(in_file: EncodedText, shift: int = 1) -> TextFile:
    contents = in_file.read_text()
    # Decode by shifting ASCII codes back by 1
    decoded_contents = "".join(chr(ord(c) - shift) for c in contents)
    out_file = TextFile.sample()
    out_file.write_text(decoded_contents)
    return out_file


@extra_implementation(MyFormat.dummy_extra)
def my_format_dummy_extra(my_format: MyFormat) -> int:
    check_optional_dependency(dummy_import)
    return 42


@extra_implementation(WithExtra.foo)
def with_extra_foo(wextra: WithExtra, an_arg: int) -> int:
    return an_arg * 2


@extra_implementation(WithExtra.generate_sample_data)
def with_extra_generate_sample_data(
    wextra: WithExtra,
    generator: SampleFileGenerator,
) -> list[Path]:
    # Generate sample data by writing some text to the file
    return [generator.generate(WithExtra, fill=10)]


@extra_implementation(Foo.generate_sample_data)
def foo_generate_sample_data(
    foo: Foo,
    generator: SampleFileGenerator,
) -> list[Path]:
    # Generate sample data by writing some text to the file
    return [generator.generate(Foo, fill=10)]
