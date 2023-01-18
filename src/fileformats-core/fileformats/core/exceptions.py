from __future__ import annotations


class FileFormatsError(RuntimeError):
    "Base exception class"


class FormatMismatchError(RuntimeError):
    "File formats don't match"


class FormatConversionError(RuntimeError):
    "No converters exist between formats"


class UnrecognisedMimeTypeError(KeyError):
    "Did not find a format class corresponding to a MIME, or MIME-like, type string"
