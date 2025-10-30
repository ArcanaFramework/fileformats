from pydra.compose import python

from fileformats.core import converter, extra_implementation
from fileformats.extras.core import check_optional_dependency
from fileformats.testing import AbstractFile, ConvertibleToFile, EncodedText, MyFormat
from fileformats.text import TextFile

dummy_import = None


@converter  # pyright: ignore[reportArgumentType]
@python.define(outputs=["out_file"])  # type: ignore[misc]
def ConvertibleToConverter(in_file: AbstractFile) -> ConvertibleToFile:
    return ConvertibleToFile.sample()


@converter  # pyright: ignore[reportArgumentType]
@python.define(outputs=["out_file"])  # type: ignore[misc]
def EncodedFromTextConverter(in_file: TextFile, shift: int = 1) -> EncodedText:
    contents = in_file.read_text()
    # Encode by shifting ASCII codes forward by 1
    encoded_contents = "".join(chr(ord(c) + shift) for c in contents)
    out_file = EncodedText.sample()
    out_file.write_text(encoded_contents)
    return out_file


@converter  # pyright: ignore[reportArgumentType]
@python.define(outputs=["out_file"])  # type: ignore[misc]
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
