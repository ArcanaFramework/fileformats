import imageio
import numpy  # noqa: F401
import typing  # noqa: F401
from fileformats.core import extra_implementation
from fileformats.image.raster import RasterImage, DataArrayType


@extra_implementation(RasterImage.load)
def read_raster_data(image: RasterImage) -> DataArrayType:
    return imageio.imread(image.fspath)  # type: ignore


@extra_implementation(RasterImage.save)
def write_raster_data(image: RasterImage, data: DataArrayType) -> None:
    imageio.imwrite(image.fspath, data)
