from ..core import __version__
from .raster import RasterImage, Bitmap, Gif, Jpeg, Png, Tiff
from .vector import VectorImage, Svg

try:
    from .converters import *
except ImportError:
    f"could not import converters for {__name__}  module, please install with the"
    f"'extended' install extra to use converters for {__name__}, i.e.\n\n"
    "$ python3 -m pip install fileformats-medimage[extended]"
