from .base import Image
from fileformats.serialization import Xml


class VectorImage(Image):
    iana_mime = None


class Svg(VectorImage, Xml):
    ext = ".svg"
    iana_mime = "image/svg+xml"
