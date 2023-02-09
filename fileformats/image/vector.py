from .base import Image
from fileformats.serialization import Xml


class VectorImage(Image):
    iana_mime = None


class Svg__Xml(VectorImage, Xml):
    ext = ".svg"
    iana_mime = "image/svg+xml"


Svg = Svg__Xml  # Alias image/svg to image/svg+xml
