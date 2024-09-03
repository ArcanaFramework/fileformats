import imageio
from fileformats.image.raster import RasterImage, DataArrayType


@RasterImage.read_data.register
def read_raster_data(image: RasterImage) -> DataArrayType:
    return imageio.imread(image.fspath)  # type: ignore


@RasterImage.write_data.register
def write_raster_data(image: RasterImage, data_array: DataArrayType) -> None:
    imageio.imwrite(image.fspath, data_array)
