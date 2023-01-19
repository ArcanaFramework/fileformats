from ..core import __version__
from fileformats.generic import File


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
