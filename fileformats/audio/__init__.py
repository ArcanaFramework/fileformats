from ..core import __version__
from fileformats.generic import File


class Audio(File):
    "Base class for audio file formats"
    binary = True
    iana_mime = None


# Compressed formats
class Mpeg(Audio):
    ext = ".mp3"
    alternate_exts = (".mp1", ".mp2")
    iana_mime = "audio/mpeg"


class Mp4(Audio):
    ext = ".mp4"
    iana_mime = "audio/mp4"


class Aac(Audio):
    ext = ".aac"
    alternate_exts = (".adts", ".loas", ".ass")
    iana_mime = "audio/aac"


class Wav(Audio):
    ext = ".wav"
    iana_mime = "audio/wav"
