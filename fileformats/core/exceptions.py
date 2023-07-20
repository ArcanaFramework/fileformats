class FileFormatsError(RuntimeError):
    "Base exception class"


class FormatMismatchError(FileFormatsError):
    "File formats don't match"


class FormatConversionError(FileFormatsError):
    "No converters exist between formats"


class FormatRecognitionError(KeyError, FileFormatsError):
    "Did not find a format class corresponding to a MIME, or MIME-like, type string"


class MissingExtendedDepenciesError(FileFormatsError):
    "'extended' install extra wasn't installed required for advanced behaviour"


class FileFormatsExtrasError(FileFormatsError):
    """If there is an "extras hook" in the datatype class but no methods have been
    registered on it"""


class FileFormatsExtrasPkgUninstalledError(FileFormatsExtrasError):
    """If there is an "extras hook" in the datatype class and a extras package on PyPI
    but it hasn't been installed"""


class FileFormatsExtrasPkgNotCheckedError(FileFormatsExtrasError):
    """If there is an "extras hook" in the datatype class and a extras package on PyPI
    but it hasn't been installed"""
