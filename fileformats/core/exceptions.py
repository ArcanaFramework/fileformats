from __future__ import annotations


class FileFormatError(Exception):
    pass


class FileFormatConversionError(Exception):
    "No converters exist between formats"


class FilePathsNotSetException(Exception):
    pass
