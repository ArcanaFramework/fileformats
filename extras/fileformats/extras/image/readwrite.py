import imageio
from fileformats.image.raster import RasterImage


@RasterImage.read_data.register
def read_raster_data(image: RasterImage):
    return imageio.imread(image.fspath)


@RasterImage.write_data.register
def write_raser_data(image: RasterImage, data_array):
    imageio.imwrite(image.fspath, data_array)
