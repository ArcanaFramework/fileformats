from pathlib import Path
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
    file.flag = 1
    assert file.cached_prop == 0
    fspath.write_text("world")
    assert file.cached_prop == 1
