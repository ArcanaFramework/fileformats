from ..core import __version__
from fileformats.generic import File


class TextMatrix(File):
    ext = ".mat"


class RFile(File):
    ext = ".rData"
    binary = True


class MatlabMatrix(File):
    ext = ".mat"


class DataFile(File):
    """Generic binary data file"""

    binary = True
    ext = ".dat"
