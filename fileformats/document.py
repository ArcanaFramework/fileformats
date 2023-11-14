from warnings import warn
from fileformats.application.document import *  # noqa

warn(
    "Importing directly from `fileformats.application` has been deprecated, please "
    "import file format classes from `fileformats.application` instead"
)
