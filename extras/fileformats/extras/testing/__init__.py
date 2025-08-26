from fileformats.core import converter
from fileformats.testing import AbstractFile, ConvertibleToFile
from pydra.compose import python


@converter
@python.define(outputs={"out_file": ConvertibleToFile})  # type: ignore[misc]
def ConvertibleToConverter(in_file: AbstractFile):
    return ConvertibleToFile.sample()
