from _version import __version__
from fileformats.core import File


class TextMatrix(File):
    ext = ".mat"


class RFile(File):
    ext = ".rData"


class MatlabMatrix(File):
    ext = ".mat"
