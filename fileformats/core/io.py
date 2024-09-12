import io
import typing as ty
from types import TracebackType


class BinaryIOWindow(ty.BinaryIO):
    """Presents a window onto an underlying BinaryIO object in a duck-typable
    subclass, so functions that take a stream object can be presented a partial view
    onto a file-stream. Can be useful where a header file is appended to a binary file
    e.g. DICOM header on Siemens raw PET data files.

    Parameters
    ----------
    binary_io: ty.BinaryIO
        the base stream to be windowed
    start: int
        start of the window, if negative then interpreted as being from the end of the stream
    end: int, optional
        end of the window, if negative then interpreted as being from the end of the stream,
        if None then the end of the stream, by default None
    """

    wrapped_io: ty.BinaryIO
    start: int
    end: int

    def __init__(
        self, binary_io: ty.BinaryIO, start: int, end: ty.Optional[int] = None
    ):
        if binary_io.seekable() is False:
            binary_io = io.BytesIO(binary_io.read())
        self.wrapped_io = binary_io
        self.wrapped_io.seek(0, io.SEEK_END)
        file_size = self.wrapped_io.tell()
        if end is None:
            end = file_size
        if start >= 0:
            self.start = start
        else:
            self.start = file_size + start
            if self.start < 0:
                raise ValueError(
                    f"Start position {start} is before the start of the file ({file_size})"
                )
        if end >= 0:
            if end > file_size:
                raise ValueError(
                    f"End position {end} is beyond end of the file ({file_size})"
                )
            self.end = end
        else:
            self.end = file_size + end
        if self.end < self.start:
            raise ValueError(
                f"End position, {end}, is before start position, {start}, for file of "
                f"size {file_size}"
            )
        self.size = self.end - self.start
        self.wrapped_io.seek(self.start)

    def read(self, size: ty.Optional[int] = -1) -> bytes:
        current_pos = self.tell()
        if current_pos >= self.size:
            return b""
        if size is None or size < 0 or (current_pos + size) > self.size:
            size = self.size - current_pos
        return self.wrapped_io.read(size)

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            ref = self.start
        elif whence == io.SEEK_CUR:
            ref = self.wrapped_io.tell()
        elif whence == io.SEEK_END:
            ref = self.end
        else:
            raise ValueError(
                f"Invalid value for 'whence' {whence}, should be 0, 1, or 2 "
                "(io.SEEK_SET, io.SEEK_CUR, io.SEEK_END)"
            )
        return self.wrapped_io.seek(ref + offset)

    def tell(self) -> int:
        return self.wrapped_io.tell() - self.start

    def __iter__(self) -> ty.Iterator[bytes]:
        self.seek(0)
        return self

    def __next__(self) -> bytes:
        line = self.readline()
        if not line:
            raise StopIteration
        return line

    @property
    def mode(self) -> str:
        return self.wrapped_io.mode

    @property
    def name(self) -> str:
        return self.wrapped_io.name

    def close(self) -> None:
        self.wrapped_io.close()

    @property
    def closed(self) -> bool:
        return self.wrapped_io.closed

    def fileno(self) -> int:
        return self.wrapped_io.fileno()

    def flush(self) -> None:
        raise NotImplementedError

    def isatty(self) -> bool:
        return self.wrapped_io.isatty()

    def readable(self) -> bool:
        return self.wrapped_io.readable()

    def readline(self, limit: int = -1) -> bytes:
        current_pos = self.tell()
        if current_pos >= self.size:
            return b""
        line = self.wrapped_io.readline()
        if current_pos + len(line) > self.size:
            line = line[: (self.size - current_pos)]
        return line

    def readlines(self, hint: int = -1) -> ty.List[bytes]:
        lines = []
        total_bytes = 0
        for line in self:
            lines.append(line)
            total_bytes += len(line)
            if hint > 0 and total_bytes >= hint:
                break
        return lines

    def seekable(self) -> bool:
        assert self.wrapped_io.seekable()
        return True

    def truncate(self, size: ty.Optional[int] = None) -> int:
        raise NotImplementedError

    def writable(self) -> bool:
        return False

    def write(self, s: bytes) -> int:  # type: ignore[override]
        raise NotImplementedError

    def writelines(self, lines: ty.Iterable[bytes]) -> None:  # type: ignore[override]
        raise NotImplementedError

    def __enter__(self) -> ty.BinaryIO:
        self.wrapped_io.__enter__()
        return self

    def __exit__(
        self,
        type: ty.Optional[ty.Type[BaseException]],
        value: ty.Optional[BaseException],
        traceback: ty.Optional[TracebackType],
    ) -> None:
        return self.wrapped_io.__exit__(type, value, traceback)
