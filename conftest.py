import os
import logging
from pathlib import Path
import tempfile
import pytest
import xnat4tests
from click.testing import CliRunner

# Set DEBUG logging for unittests

log_level = logging.WARNING

logger = logging.getLogger("arcana")
logger.setLevel(log_level)

sch = logging.StreamHandler()
sch.setLevel(log_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sch.setFormatter(formatter)
logger.addHandler(sch)


TEST_AWS_BUCKET = os.getenv("TEST_AWS_BUCKET", None)


# For debugging in IDE's don't catch raised exceptions and let the IDE
# break at it
if os.getenv("_PYTEST_RAISE", "0") != "0":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call):
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo):
        raise excinfo.value

    CATCH_CLI_EXCEPTIONS = False
else:
    CATCH_CLI_EXCEPTIONS = True


@pytest.fixture
def catch_cli_exceptions():
    return CATCH_CLI_EXCEPTIONS


@pytest.fixture(scope="session")
def xnat_archive_dir():

    xnat4tests.start_xnat()
    xnat4tests.add_data("dummydicom")
    return xnat4tests.Config().xnat_root_dir / "archive"


@pytest.fixture
def cli_runner(catch_cli_exceptions):
    def invoke(*args, catch_exceptions=catch_cli_exceptions, **kwargs):
        runner = CliRunner()
        result = runner.invoke(*args, catch_exceptions=catch_exceptions, **kwargs)
        return result

    return invoke


@pytest.fixture
def work_dir():
    work_dir = tempfile.mkdtemp()
    return Path(work_dir)
