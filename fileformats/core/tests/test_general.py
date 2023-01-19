import pytest
from fileformats.generic import File
from fileformats.core.exceptions import FileFormatsError, FormatMismatchError
from fileformats.core import mark
from conftest import write_test_file


def test_init_args(work_dir):
    fspath = work_dir / "test.txt"
    write_test_file(fspath)
    File([fspath])
    with pytest.raises(TypeError):
        File(fspath, fspath)


def test_metadata_iterator_fail(work_dir):
    fspath = work_dir / "test.txt"
    write_test_file(fspath)
    file = File(fspath)
    with pytest.raises(NotImplementedError):
        iter(file.metadata)


class TestFile(File):

    ext = ".tst"


def test_multiple_matches1(work_dir):
    fspath1 = work_dir / "test1.tst"
    write_test_file(fspath1)
    fspath2 = work_dir / "test2.tst"
    write_test_file(fspath2)
    with pytest.raises(FormatMismatchError):
        File([fspath1, fspath2])


def test_multiple_matches2(work_dir):
    fspath1 = work_dir / "test1.tst"
    write_test_file(fspath1)
    fspath2 = work_dir / "test2.tst"
    write_test_file(fspath2)
    with pytest.raises(FormatMismatchError):
        TestFile([fspath1, fspath2])


def test_missing_files(work_dir):
    fspath = work_dir / "test.tst"
    write_test_file(fspath)
    # with pytest.raises(FileNotFoundError):
    TestFile([fspath, work_dir / "missing1.txt", work_dir / "missing2.txt"])


class ImageWithInlineHeader(File):

    ext = ".img"
    binary = True

    header_separator = b"---END HEADER---"

    def load_metadata(self):
        hdr = self.contents.split(self.header_separator)[0].decode("utf-8")
        return {k: int(v) for k, v in (ln.split(":") for ln in hdr.splitlines())}


def test_header_overwrite(work_dir):

    fspath = work_dir / "image.img"
    hdr = {
        "x": 10,
        "y": 20,
    }
    write_test_file(
        fspath,
        (
            "\n".join(f"{k}:{v}" for k, v in hdr.items()).encode("utf-8")
            + ImageWithInlineHeader.header_separator
            + b"SOMERANDOMBYTESDATA"
        ),
        binary=True,
    )
    file = ImageWithInlineHeader(fspath, metadata={"x": "100"})
    with pytest.raises(FileFormatsError):
        file.metadata["y"]


class YFile(ImageWithInlineHeader):
    @mark.required
    @property
    def y(self):
        return self.metadata["y"]

    @mark.check
    def y_value(self):
        if self.y <= 10:
            raise FormatMismatchError(f"'y' property is not > 10 ({self.y})")


def test_required_check_op(work_dir):
    fspath = work_dir / "image.img"
    hdr = {
        "x": 10,
        "y": 20,
    }
    write_test_file(
        fspath,
        (
            "\n".join(f"{k}:{v}" for k, v in hdr.items()).encode("utf-8")
            + ImageWithInlineHeader.header_separator
            + b"SOMERANDOMBYTESDATA"
        ),
        binary=True,
    )
    assert YFile.matches(fspath)


def test_required_check_op_fail(work_dir):
    fspath = work_dir / "image.img"
    hdr = {
        "x": 10,
        "y": 10,
    }
    write_test_file(
        fspath,
        (
            "\n".join(f"{k}:{v}" for k, v in hdr.items()).encode("utf-8")
            + ImageWithInlineHeader.header_separator
            + b"SOMERANDOMBYTESDATA"
        ),
        binary=True,
    )
    assert not YFile.matches(fspath)
