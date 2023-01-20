from __future__ import annotations
from pathlib import Path
from . import mark
from .base import FileSet
from .exceptions import FileFormatsError, FormatMismatchError


class WithMagicNumber:
    """Mixin class for Files with magic numbers at the start of their
    contents.

    Class Attrs
    -----------
    magic_number : str
        the magic number/string to search for at the start of the file
    binary : bool
        if the file-format is a binary type then this flag needs to be set in order to
        read the contents properly
    magic_number_offset : int, optional
        the offset in bytes from the start of the file that the magic number is stored
    """

    magic_number_offset = 0

    @mark.check
    def check_magic_number(self):
        if self.binary and isinstance(self.magic_number, str):
            magic_bytes = bytes.fromhex(self.magic_number)
        else:
            magic_bytes = self.magic_number
        read_magic_number = self.read_contents(
            len(magic_bytes), offset=self.magic_number_offset
        )
        if read_magic_number != magic_bytes:
            if self.binary and isinstance(self.magic_number, str):
                read_magic_str = '"' + bytes.hex(read_magic_number) + '"'
                magic_str = '"' + self.magic_number + '"'
            else:
                read_magic_str = read_magic_number
                magic_str = self.magic_number
            raise FormatMismatchError(
                f"Magic number of file {read_magic_str} doesn't match expected "
                f"{magic_str}"
            )


class WithAdjacentFiles:
    """
    If only one fspath is provided to the __init__ of the class, this mixin automatically
    includes any "adjacent files", i.e. any files with the same stem but different
    extension

    Note that WithAdjacents must come before the primary type in the method-resolution
    order of the class so it can override the '__attrs_post_init__' method in
    post_init_super class (typically FileSet), e.g.

        class MyFileFormatWithSeparateHeader(WithSeparateHeader, MyFileFormat):

            header_type = MyHeaderType

    Class Attrs
    -----------
    post_init_super : type
        the format class the WithAdjacentFiles mixin is mixed with that defines the
        __attrs_post_init__ method that should be called once the adjacent files
        are added to the self.fspaths attribute to run checks.
    """

    post_init_super = FileSet

    def __attrs_post_init__(self):
        if len(self.fspaths) == 1:
            self.fspaths.update(self.get_adjacent_files())
            trim = True
        else:
            trim = False
        self.post_init_super.__attrs_post_init__(self)
        if trim:
            self.trim_paths()

    def get_adjacent_files(self) -> set[Path]:
        for ext in self.possible_exts:
            if not self.fspath.name.endswith(ext):
                continue
            stem = self.fspath.name[: -(len(ext))]
            adjacents = set()
            for sibling in self.fspath.parent.iterdir():
                if (
                    sibling is not self.fspath
                    and sibling.is_file()
                    and sibling.name.startswith(stem)
                ):
                    adjacents.add(sibling)
            return adjacents
        assert False, (
            f"extension of fspath {self.fspath} is not in possible extensions for "
            f"{type(self)} class: {self.possible_exts}"
        )


class WithSeparateHeader(WithAdjacentFiles):
    """Mixin class for Files with metadata stored in separate header files (typically
    with the same file stem but differing extension)

    Note that WithSeparateHeader must come before the primary type in the method-resolution
    order of the class so it can override the '__attrs_post_init__' method, e.g.

        class MyFileFormatWithSeparateHeader(WithSeparateHeader, MyFileFormat):

            header_type = MyHeaderType

    Class Attrs
    -----------
    header_type : type
        the file-format of the header file
    """

    @mark.required
    @property
    def header(self):
        return self.header_type(self.select_by_ext(self.header_type))

    def load_metadata(self):
        return self.header.load()


class WithSideCar(WithAdjacentFiles):
    """Mixin class for Files with a "side-car" file that augments the inline metadata
    (typically with the same file stem but differing extension).

    Note that WithSideCar must come before the primary type in the method-resolution
    order of the class so it can override the '__attrs_post_init__' and 'load_metadata'
    methods, e.g.

        class MyFileFormatWithSideCar(WithSideCar, MyFileFormat):

            primary_type = MyFileFormat
            side_car_type = MySideCarType

    Class Attrs
    -----------
    primary_type : type
        the file-format of the primary file (used to read the inline metadata), can be
        the base class that implements 'load_metadata'
    side_car_type : type
        the file-format of the header file
    """

    @mark.required
    @property
    def side_car(self):
        return self.side_car_type(self.select_by_ext(self.side_car_type))

    def load_metadata(self):
        metadata = self.primary_type.load_metadata(self)
        side_car_data = self.side_car.load()
        overlap = set(metadata) & set(side_car_data)
        if overlap:
            raise FileFormatsError(
                "Detected overlap between header values and side-car values:\n"
                "\n".join(
                    f"{k}: header={metadata[k]}, side-car={side_car_data[k]}"
                    for k in overlap
                )
            )
        metadata.update(side_car_data)
        return metadata
