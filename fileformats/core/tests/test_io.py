import io
import pytest
from pathlib import Path
from fileformats.core.io import BinaryIOWindow


def test_binary_window():

    data = b"0123456789abcdefghijklmnopqrstuvwxyz"
    with BinaryIOWindow(io.BytesIO(data), start=10, end=25) as window:
        assert window.read() == b"abcdefghijklmno"
        assert window.tell() == 15
        window.seek(0)
        assert window.read(3) == b"abc"
        assert window.tell() == 3
        window.seek(3, io.SEEK_CUR)
        assert window.read(3) == b"ghi"
        window.seek(-3, io.SEEK_END)
        assert window.read() == b"mno"
        window.seek(3)
        assert window.read(3) == b"def"
        assert window.tell() == 6
        with pytest.raises(ValueError):
            window.seek(0, 3)
    assert window.closed


def test_binary_window_no_end():

    data = b"0123456789abcdefghijklmnopqrstuvwxyz"
    with BinaryIOWindow(io.BytesIO(data), start=10) as window:
        assert window.read() == b"abcdefghijklmnopqrstuvwxyz"


def test_binary_window_attrs():
    data = b"abc"
    with BinaryIOWindow(io.BytesIO(data), start=1, end=-1) as window:
        assert window.readable()
        assert not window.closed
        assert window.seekable()
        assert not window.writable()


def test_binary_window_negative():
    data = b"abcdefghijklmnopqrstuvwxyz0123456789"
    with BinaryIOWindow(io.BytesIO(data), start=-20, end=-10) as window:
        assert window.read() == b"qrstuvwxyz"
        assert window.tell() == 10
        window.seek(0)
        assert window.read(3) == b"qrs"
        assert window.tell() == 3
        window.seek(-3, io.SEEK_END)
        assert window.read() == b"xyz"
        assert window.tell() == 10


def test_binary_window_readlines():
    data = b"abc\ndef\nghi\njkl\n"
    with BinaryIOWindow(io.BytesIO(data), start=4, end=-4) as window:
        assert window.readlines() == [b"def\n", b"ghi\n"]
        window.seek(0)
        assert next(window) == b"def\n"
        assert window.tell() == 4
        assert window.readline() == b"ghi\n"
        assert list(window) == [b"def\n", b"ghi\n"]


def test_binary_window_write():
    data = b"abc"
    with BinaryIOWindow(io.BytesIO(data), start=1, end=-1) as window:
        with pytest.raises(NotImplementedError):
            window.write(b"test")
        with pytest.raises(NotImplementedError):
            window.writelines([b"test"])
        with pytest.raises(NotImplementedError):
            window.truncate()
        with pytest.raises(NotImplementedError):
            window.flush()


def test_binary_window_misc(tmp_path: Path):
    test_file = tmp_path / "test.txt"
    test_file.write_bytes(b"12345abcdefghij1234567890")
    with BinaryIOWindow(test_file.open("rb"), start=5, end=-10) as window:
        assert window.read() == b"abcdefghij"
        assert window.tell() == 10
        window.seek(0)
        assert window.fileno() > 0
        assert window.mode == "rb"
        assert window.isatty() is False
        assert window.name == str(test_file)


def test_binary_window_open_close():
    data = b"abc"
    window = BinaryIOWindow(io.BytesIO(data), start=1, end=-1)
    assert not window.closed
    window.close()
    assert window.closed


def test_binary_window_end_too_big():
    with pytest.raises(ValueError, match="beyond end of the file"):
        BinaryIOWindow(io.BytesIO(b"abc"), start=0, end=4)


def test_binary_window_start_too_small():
    with pytest.raises(ValueError, match="before the start of the file"):
        BinaryIOWindow(io.BytesIO(b"abc"), start=-4)


def test_binary_window_end_before_start():
    with pytest.raises(ValueError, match=" is before start position"):
        BinaryIOWindow(io.BytesIO(b"abc"), start=1, end=-3)
