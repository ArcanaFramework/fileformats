from ..core import __version__
from fileformats.generic import File


class Video(File):
    "Base class for audio file formats"
    binary = True
    iana = None


class Mp4(Video):
    ext = ".mp4"
    iana = "video/mp4"


class Webm(Video):
    ext = ".webm"
    iana = "video/webm"


class Quicktime(Video):
    ext = ".mov"
    alternate_exts = (".qt",)
    iana = "video/quicktime"


class Ogg(Video):
    ext = ".ogv"
    iana = "video/ogg"
