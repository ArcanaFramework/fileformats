import imageio
from fileformats.core import extra_implementation
from fileformats.image.raster import RasterImage, DataArrayType


@extra_implementation(RasterImage.read_data)
def read_raster_data(image: RasterImage) -> DataArrayType:
    return imageio.imread(image.fspath)  # type: ignore


@extra_implementation(RasterImage.write_data)
def write_raster_data(image: RasterImage, data_array: DataArrayType) -> None:
    imageio.imwrite(image.fspath, data_array)
