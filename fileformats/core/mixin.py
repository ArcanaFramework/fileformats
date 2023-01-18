from __future__ import annotations
from . import mark
from .exceptions import FileFormatsError, FormatMismatchError


class WithMagic:
    """Mixin class for Files with magic numbers at the start of their
    contents.

    Required Class Attrs
    --------------------
    magic : str
        the magic number/string to search for at the start of the file
    binary : bool
        if the file-format is a binary type then this flag needs to be set in order to
        read the contents properly
    """

    magic_offset = 0

    @mark.check
    def check_magic(self):
        if self.binary and isinstance(self.magic, str):
            magic_bytes = bytes.fromhex(self.magic)
        else:
            magic_bytes = self.magic
        read_magic = self.read_contents(len(magic_bytes), offset=self.magic_offset)
        if read_magic != magic_bytes:
            if self.binary and isinstance(self.magic, str):
                read_magic_str = '"' + bytes.hex(read_magic) + '"'
                magic_str = '"' + self.magic + '"'
            else:
                read_magic_str = read_magic
                magic_str = self.magic
            raise FormatMismatchError(
                f"Magic number of file {read_magic_str} doesn't match expected "
                f"{magic_str}"
            )


class WithSeparateHeader:
    """Mixin class for Files with metadata stored in separate header files (typically
    with the same file stem but differing extension)

    Required Class Attrs
    --------------------
    header_type : type
        the file-format of the header file
    """

    @mark.required
    @property
    def header(self):
        return self.header_type(self.select_by_ext(self.header_type))

    def load_metadata(self):
        return self.header.load()


class WithSideCar:
    """Mixin class for Files with a "side-car" file that augments the inline metadata
    (typically with the same file stem but differing extension).

    Note that WithSideCar must come before the primary type in the method-resolution
    order of the class so it can override the 'load_metadata' method, e.g.

        class MyFileFormatWithSideCar(WithSideCar, MyFileFormat):

            primary_type = MyFileFormat
            side_car_type = MySideCarType

    Required Class Attrs
    --------------------
    primary_type : type
        the file-format of the primary file (used to read the inline metadata)
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
        if overlap := set(metadata) & set(side_car_data):
            raise FileFormatsError(
                "Detected overlap between header values and side-car values:\n"
                "\n".join(
                    f"{k}: header={metadata[k]}, side-car={side_car_data[k]}"
                    for k in overlap
                )
            )
        metadata.update(side_car_data)
        return metadata
