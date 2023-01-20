from fileformats.generic import File
from fileformats.core.mixin import WithSeparateHeader
from fileformats.core.utils import matching_formats
import fileformats.text
import fileformats.numeric
from conftest import write_test_file


class Bar(File):

    ext = ".bar"


class Foo(WithSeparateHeader, File):

    ext = ".foo"
    header_type = Bar


def test_copy(work_dir):

    foo_fspath = work_dir / "x.foo"
    write_test_file(foo_fspath)
    bar_fspath = work_dir / "y.bar"
    write_test_file(bar_fspath)
    file = Foo([foo_fspath, bar_fspath])
    dest_dir = work_dir / "new-dir"
    dest_dir.mkdir()
    cpy = file.copy_to(dest_dir)
    assert cpy.fspath.parent == dest_dir
    assert cpy.fspath.name == "x.foo"
    assert cpy.header.fspath.parent == dest_dir
    assert cpy.header.fspath.name == "y.bar"


def test_copy_with_rename(work_dir):

    foo_fspath = work_dir / "x.foo"
    write_test_file(foo_fspath)
    bar_fspath = work_dir / "y.bar"
    write_test_file(bar_fspath)
    file = Foo([foo_fspath, bar_fspath])
    cpy = file.copy_to(work_dir, stem="new")
    assert cpy.fspath.name == "new.foo"
    assert cpy.header.fspath.name == "new.bar"


def test_copy_symlink(work_dir):

    foo_fspath = work_dir / "x.foo"
    write_test_file(foo_fspath)
    bar_fspath = work_dir / "y.bar"
    write_test_file(bar_fspath)
    file = Foo([foo_fspath, bar_fspath])
    dest_dir = work_dir / "new-dir"
    dest_dir.mkdir()
    cpy = file.copy_to(dest_dir, symlink=True)
    assert cpy.fspath.parent == dest_dir
    assert cpy.fspath.name == "x.foo"
    assert cpy.header.fspath.parent == dest_dir
    assert cpy.header.fspath.name == "y.bar"


def test_copy_ext(work_dir):
    assert (
        File.copy_ext(work_dir / "x.foo.bar", work_dir / "y") == work_dir / "y.foo.bar"
    )
    assert Bar.copy_ext(work_dir / "x.foo.bar", work_dir / "y") == work_dir / "y.bar"


def test_format_detection(work_dir):

    text_file = work_dir / "text.txt"

    with open(text_file, "w") as f:
        f.write("sample text")

    detected = matching_formats(text_file)
    assert len(detected) == 1
    assert detected[0] is fileformats.text.Plain

    # dat_file = work_dir / "data.dat"

    # with open(dat_file, "wb") as f:
    #     f.write(b"sample bytes")

    # assert detect_format(dat_file) is fileformats.numeric.DataFile
