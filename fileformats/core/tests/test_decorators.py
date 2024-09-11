from pathlib import Path
import time
from fileformats.core.decorators import mtime_cached_property
from fileformats.generic import File


class MtimeTestFile(File):

    flag: int

    @mtime_cached_property
    def cached_prop(self):
        return self.flag


def test_mtime_cached_property(tmp_path: Path):
    fspath = tmp_path / "file_1.txt"
    fspath.write_text("hello")

    file = MtimeTestFile(fspath)

    file.flag = 0
    assert file.cached_prop == 0
    # Need a long delay to ensure the mtime changes on Ubuntu and particularly on Windows
    # On MacOS, the mtime resolution is much higher so not usually an issue. Use
    # explicitly cache clearing if needed
    time.sleep(2)
    file.flag = 1
    assert file.cached_prop == 0
    time.sleep(2)
    fspath.write_text("world")
    assert file.cached_prop == 1


def test_mtime_cached_property_force_clear(tmp_path: Path):
    fspath = tmp_path / "file_1.txt"
    fspath.write_text("hello")

    file = MtimeTestFile(fspath)

    file.flag = 0
    assert file.cached_prop == 0
    file.flag = 1
    MtimeTestFile.cached_prop.clear(file)
    assert file.cached_prop == 1
