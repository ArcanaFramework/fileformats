import imageio
import typing as ty
import numpy  # noqa: F401
import typing  # noqa: F401
from fileformats.core import FileSet, extra_implementation
from fileformats.image.raster import RasterImage, DataArrayType


@extra_implementation(FileSet.load)
def read_raster_data(image: RasterImage, **kwargs: ty.Any) -> DataArrayType:
    return imageio.imread(image.fspath)  # type: ignore


@extra_implementation(FileSet.save)
def write_raster_data(
    image: RasterImage, data: DataArrayType, **kwargs: ty.Any
) -> None:
    imageio.imwrite(image.fspath, data, **kwargs)
