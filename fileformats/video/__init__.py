from ..core import __version__
from fileformats.generic import File


class Video(File):
    "Base class for audio file formats"
    binary = True
    iana_mime = None


class Mp4(Video):
    ext = ".mp4"
    iana_mime = "video/mp4"


class Webm(Video):
    ext = ".webm"
    iana_mime = "video/webm"


class Quicktime(Video):
    ext = ".mov"
    alternate_exts = (".qt",)
    iana_mime = "video/quicktime"


class Ogg(Video):
    ext = ".ogv"
    iana_mime = "video/ogg"
