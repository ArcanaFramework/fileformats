class FileFormatError(Exception):
    pass


class FileFormatConversionError(Exception):
    "No converters exist between formats"


class NamedError(Exception):
    def __init__(self, name, msg):
        super().__init__(msg)
        self.name = name


class DataNotDerivedYetError(NamedError):
    pass


class NameError(NamedError):
    pass


class FilePathsNotSetException(Exception):
    pass
