from __future__ import annotations


class FileFormatsError(RuntimeError):
    "Base exception class"


class FormatMismatchError(FileFormatsError):
    "File formats don't match"


class FormatConversionError(FileFormatsError):
    "No converters exist between formats"
