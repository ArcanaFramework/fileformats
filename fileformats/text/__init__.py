from ..core import __version__
from fileformats.generic import File
from fileformats.serialization import (
    Json,
    Xml,
    Yaml,
)  # These are sometimes/historically considered part of the text registry so we import them here


# General formats
class Plain(File):
    ext = ".txt"
    iana_mime = "text/plain"


class Csv(File):
    ext = ".csv"
    iana_mime = "text/csv"


class Tsv(File):
    ext = ".tsv"
    iana_mime = "text/tsv"


class Html(File):
    ext = ".html"
    alternate_exts = (".htm",)
    iana_mime = "text/html"


class Markdown(File):
    ext = ".md"
    iana_mime = "text/markdown"


class RestructedText(File):
    ext = ".rst"
    iana_mime = "text/x-rst"
