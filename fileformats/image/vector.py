from .base import Image
from fileformats.application import InformalSchema, Xml


class VectorImage(Image):
    iana_mime = None


class Svg(InformalSchema):
    pass


class Svg__Xml(VectorImage, Xml):
    ext = ".svg"
    iana_mime = "image/svg+xml"
    schema = Svg  # Set Xml schema attribute
    classifiers_attr_name = None  # disable classifiers inherited from Xml
