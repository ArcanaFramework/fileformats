import pytest

# from fileformats.core.generic import File
# from fileformats.core.exceptions import FileFormatsError, FormatMismatchError
# from fileformats.core import mark
# from conftest import write_test_file

try:
    import pydra
except ImportError:
    pydra = None


@pytest.mark.skipIf(pydra is None, "Pydra could not be imported")
def test_find_converter(work_dir):
    pass
