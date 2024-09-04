import typing as ty
import pytest
import time
from fileformats.core import FileSet, extra_implementation
from fileformats.generic import File


class FileWithMetadata(File):
    ext = ".mf"


@extra_implementation(FileSet.read_metadata)
def aformat_read_metadata(
    mf: FileWithMetadata, selected_keys: ty.Optional[ty.Collection[str]] = None
) -> ty.Mapping[str, ty.Any]:
    with open(mf) as f:
        metadata = f.read()
    dct = dict(ln.split(":") for ln in metadata.splitlines())
    if selected_keys:
        dct = {k: v for k, v in dct.items() if k in selected_keys}
    return dct


@pytest.fixture
def file_with_metadata_fspath(tmp_path):
    metadata = {
        "a": 1,
        "b": 2,
        "c": 3,
        "d": 4,
        "e": 5,
    }
    fspath = tmp_path / "metadata-file.mf"
    with open(fspath, "w") as f:
        f.write("\n".join("{}:{}".format(*t) for t in metadata.items()))
    return fspath


def test_metadata(file_with_metadata_fspath):
    file_with_metadata = FileWithMetadata(file_with_metadata_fspath)
    assert file_with_metadata.metadata["a"] == "1"
    assert sorted(file_with_metadata.metadata) == ["a", "b", "c", "d", "e"]


def test_select_metadata(file_with_metadata_fspath):
    file_with_metadata = FileWithMetadata(
        file_with_metadata_fspath, metadata_keys=["a", "b", "c"]
    )
    assert file_with_metadata.metadata["a"] == "1"
    assert sorted(file_with_metadata.metadata) == ["a", "b", "c"]


def test_explicit_metadata(file_with_metadata_fspath):
    file_with_metadata = FileWithMetadata(
        file_with_metadata_fspath,
        metadata={
            "a": 1,
            "b": 2,
            "c": 3,
        },
    )
    # Check that we use the explicitly provided metadata and not one from the file
    # contents
    assert sorted(file_with_metadata.metadata) == ["a", "b", "c"]
    # add new metadata line to check and check that it isn't reloaded
    with open(file_with_metadata, "a") as f:
        f.write("\nf:6")
    assert sorted(file_with_metadata.metadata) == ["a", "b", "c"]


def test_metadata_reload(file_with_metadata_fspath):
    file_with_metadata = FileWithMetadata(file_with_metadata_fspath)
    assert sorted(file_with_metadata.metadata) == ["a", "b", "c", "d", "e"]
    # add new metadata line to check and check that it is reloaded
    time.sleep(2)
    with open(file_with_metadata, "a") as f:
        f.write("\nf:6")
    assert sorted(file_with_metadata.metadata) == ["a", "b", "c", "d", "e", "f"]
