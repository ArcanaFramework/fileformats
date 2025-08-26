from fileformats.core import converter
from fileformats.testing import AbstractFile, ConvertibleToFile
from pydra.compose import python


@converter  # pyright: ignore[reportArgumentType]
@python.define(outputs=["out_file"])  # type: ignore[misc]
def ConvertibleToConverter(in_file: AbstractFile) -> ConvertibleToFile:
    return ConvertibleToFile.sample()
