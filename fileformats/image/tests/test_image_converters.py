import pytest
from imageio.core.fetching import get_remote_file
from fileformats.image import Bitmap, Gif, Jpeg, Png, Tiff


@pytest.fixture(scope="session")
def jpg() -> Jpeg:
    # imageio.imread("imageio:bricks.jpg")
    return Jpeg(get_remote_file("images/bricks.jpg"))


@pytest.fixture(scope="session")
def png() -> Png:
    return Png(get_remote_file("images/chelsea.png"))


def test_jpg_to_gif(jpg):
    Gif.convert(jpg)


def test_png_to_tiff(png):
    Tiff.convert(png)


def test_png_to_bitmap(png):
    Bitmap.convert(png)
