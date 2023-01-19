import filecmp
import pytest
from fileformats.generic import File, Directory
from fileformats.archive import Zip, Gzip, Tar, Tar_Gzip


TEST_DIR = "__test_dir__"
TEST_FILE = "__test_file__.txt"

INPUT_TYPES = ["file", "directory"]


@pytest.fixture(params=INPUT_TYPES)
def archive_input(work_dir, request):
    if request.param == "file":
        test_file = work_dir / TEST_FILE
        with open(test_file, "w") as f:
            f.write("test file contents")
        inpt = File(test_file)
    elif request.param == "directory":
        test_dir = work_dir / TEST_DIR
        test_dir.mkdir()
        for i in range(1, 3):
            with open(test_dir / f"file{i}.txt", "w") as f:
                f.write(f"test file {i}")
        sub_dir = test_dir / "sub-dir"
        sub_dir.mkdir()
        for i in range(4, 6):
            with open(sub_dir / f"file{i}.txt", "w") as f:
                f.write(f"test file {i}")
        inpt = Directory(test_dir)
    else:
        assert False, f"Unrecognised request param {request.param}"
    inpt.validate()
    return inpt


def test_zip_roundtrip(archive_input):
    _roundtrip(archive_input, Zip)


@pytest.mark.xfail(reason="Gzip converter is not implemented yet")
def test_gzip_roundtrip(archive_input):
    _roundtrip(archive_input, Gzip)


def test_tar_roundtrip(archive_input):
    _roundtrip(archive_input, Tar)


def test_tar_gz_roundtrip(archive_input):
    _roundtrip(archive_input, Tar_Gzip)


def _roundtrip(input, archive_klass):
    archive = archive_klass.convert(input)
    assert isinstance(archive, archive_klass)
    archive.validate()
    output = type(input).convert(archive)
    output.validate()
    if isinstance(input, File):
        assert filecmp.cmp(output.fspath, input.fspath)
    else:
        _assert_extracted_dir_matches(output, input)


def _assert_extracted_dir_matches(extracted: Directory, reference: Directory):
    def assert_exact_match(cmp):
        assert (
            not cmp.left_only
        ), f"{cmp.left_only} missing from unarchved dir {cmp.right}"
        assert not cmp.right_only, (
            f"Additional {cmp.right_only} found in unarchived dir " + cmp.right
        )
        for subdir in cmp.subdirs.values():
            assert_exact_match(subdir)

    assert_exact_match(filecmp.dircmp(reference.fspath, extracted.fspath))
