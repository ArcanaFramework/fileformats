from ._version import __version__
from .classifier import Classifier
from .datatype import DataType
from .fileset import FileSet, MockMixin
from .field import Field
from .identification import (
    to_mime,
    from_mime,
    find_matching,
    from_paths,
)
from .sampling import SampleFileGenerator
from .extras import extra, converter

__all__ = [
    "__version__",
    "Classifier",
    "DataType",
    "FileSet",
    "MockMixin",
    "Field",
    "to_mime",
    "from_mime",
    "find_matching",
    "from_paths",
    "SampleFileGenerator",
    "extra",
    "converter",
]
