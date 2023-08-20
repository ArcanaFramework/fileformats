import sys
import shutil
import pytest
from imageio.core.fetching import get_remote_file
from fileformats.image import Png, Tiff
from fileformats.core.exceptions import FormatMismatchError

sys.version_info[1]


@pytest.fixture(scope="session")
def png_path():
    return get_remote_file("images/chelsea.png")


@pytest.mark.xfail(
    condition=sys.version_info.minor < 10,
    reason="waiting on next Pydra release for bug-fix",
)
def test_tiff_endianness(png_path):
    png = Png(png_path)
    Tiff.convert(png)


def test_tiff_fail(png_path, work_dir):
    bad_tiff_path = work_dir / "bad_tiff.tiff"
    shutil.copyfile(png_path, bad_tiff_path)
    with pytest.raises(FormatMismatchError):
        Tiff(bad_tiff_path)
