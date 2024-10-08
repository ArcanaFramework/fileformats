from pathlib import Path
import platform
import pytest
import typing as ty
from fileformats.core import validated_property
from fileformats.generic import File, UnicodeFile, BinaryFile
from fileformats.field import Integer, Boolean, Decimal, Array, Text
from fileformats.testing import Foo
from fileformats.core.exceptions import FormatMismatchError
from conftest import write_test_file


def test_init_args(work_dir):
    fspath = work_dir / "test.txt"
    write_test_file(fspath)
    UnicodeFile([fspath])


class TestFile(UnicodeFile):

    ext = ".tst"


def test_file_repr():
    if platform.system() == "Windows":
        expected = f"Foo('{Path().cwd().drive}\\mock\\foo.foo')"
    else:
        expected = "Foo('/mock/foo.foo')"
    assert repr(Foo.mock()) == expected


def test_field_repr():
    assert repr(Integer(1)) == "Integer(1)"
    assert repr(Decimal("1.1")) == "Decimal(1.1)"
    assert repr(Boolean(1)) == "Boolean(true)"
    assert repr(Text(1)) == 'Text("1")'
    assert repr(Array[Integer]([1, 2, 3])) == "Array[Integer]([1,2,3])"


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
    with pytest.raises(FileNotFoundError):
        TestFile([fspath, work_dir / "missing1.txt", work_dir / "missing2.txt"])


def test_python_hash_fileset(work_dir: Path):

    a_path = work_dir / "a.txt"
    a_path.write_text("a")
    a = File(a_path)
    a2 = File(a_path)
    b_path = work_dir / "b.txt"
    b_path.write_text("b")
    b = File(b_path)

    assert hash(a) == hash(a2)
    assert hash(b) != hash(a)


def test_python_hash_integer():

    a = Integer(1)
    a2 = Integer(1)
    b = Integer(2)

    assert hash(a) == hash(a2)
    assert hash(b) != hash(a)


def test_python_hash_decimal():

    a = Decimal(1)
    a2 = Decimal(1)
    b = Decimal(2)

    assert hash(a) == hash(a2)
    assert hash(b) != hash(a)


def test_python_hash_boolean():

    a = Boolean(1)
    a2 = Boolean(1)
    b = Boolean(0)

    assert hash(a) == hash(a2)
    assert hash(b) != hash(a)


def test_python_hash_text():

    a = Text("1")
    a2 = Text("1")
    b = Text("2")

    assert hash(a) == hash(a2)
    assert hash(b) != hash(a)


def test_python_hash_array():

    a = Array[Integer]([1, 2])
    a2 = Array[Integer]([1, 2])
    b = Array[Integer]([1, 2, 3])

    assert hash(a) == hash(a2)
    assert hash(b) != hash(a)


class ImageWithInlineHeader(BinaryFile):

    ext = ".img"

    header_separator = b"---END HEADER---"

    def read_metadata(self, **kwargs: ty.Any) -> ty.Mapping[str, ty.Any]:
        hdr = self.raw_contents.split(self.header_separator)[0].decode("utf-8")
        return {k: int(v) for k, v in (ln.split(":") for ln in hdr.splitlines())}


@pytest.mark.xfail(reason="Disabled separate header metadata")
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
    with pytest.raises(FormatMismatchError):
        file.metadata["y"]


class YFile(ImageWithInlineHeader):
    @validated_property
    def y(self):
        return self.metadata["y"]

    @validated_property
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
