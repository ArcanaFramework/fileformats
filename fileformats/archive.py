from warnings import warn
from fileformats.application.archive import *  # noqa


warn(
    "Importing directly from `fileformats.archive` has been deprecated, please "
    "import file format classes from `fileformats.application` instead"
)
