from ..core import __version__
from fileformats.generic import File
from fileformats.serialization import (
    Json,
    Xml,
    Yaml,
)  # These are sometimes considered part of the text registry so we import them here


# General formats
class Plain(File):
    ext = ".txt"


class Csv(File):
    ext = ".csv"


class Tsv(File):
    ext = ".tsv"


class Html(File):
    ext = ".html"
    alternate_exts = (".htm",)
