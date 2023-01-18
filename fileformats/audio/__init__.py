from ..core import __version__
from fileformats.core import File


class Audio(File):
    "Base class for audio file formats"
    binary = True
    iana = None


# Compressed formats
class Mpeg(Audio):
    ext = ".mp3"
    alternate_exts = (".mp1", ".mp2")
    iana = "audio/mpeg"


class Mp4(Audio):
    ext = ".mp4"
    iana = "audio/mp4"


class Aac(Audio):
    ext = ".aac"
    alternate_exts = (".adts", ".loas", ".ass")
    iana = "audio/aac"


class Wav(Audio):
    ext = ".wav"
    iana = "audio/wav"
