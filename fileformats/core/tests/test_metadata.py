import typing as ty
import pytest
from fileformats.core import FileSet
from fileformats.generic import File


class FileWithMetadata(File):
    ext = ".mf"


@FileSet.read_metadata.register
def aformat_read_metadata(
    mf: FileWithMetadata, selected_keys: ty.Optional[ty.Sequence[str]] = None
) -> ty.Mapping[str, ty.Any]:
    with open(mf) as f:
        metadata = f.read()
    dct = dict(ln.split(":") for ln in metadata.splitlines())
    if selected_keys:
        dct = {k: v for k, v in dct.items() if k in selected_keys}
    return dct


@pytest.fixture
def file_with_metadata(tmp_path):
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
    return FileWithMetadata(fspath)


def test_metadata(file_with_metadata):
    assert file_with_metadata.metadata["a"] == "1"
    assert sorted(file_with_metadata.metadata) == ["a", "b", "c", "d", "e"]


def test_select_metadata(file_with_metadata):
    file_with_metadata.select_metadata(["a", "b", "c"])
    assert file_with_metadata.metadata["a"] == "1"
    assert sorted(file_with_metadata.metadata) == ["a", "b", "c"]


def test_select_metadata_reload(file_with_metadata):
    file_with_metadata.select_metadata(["a", "b", "c"])
    assert sorted(file_with_metadata.metadata) == ["a", "b", "c"]
    # add new metadata line to check that it isn't loaded
    with open(file_with_metadata, "a") as f:
        f.write("\nf:6")
    file_with_metadata.select_metadata(["a", "b"])
    assert sorted(file_with_metadata.metadata) == ["a", "b", "c"]
    file_with_metadata.select_metadata(None)
    assert sorted(file_with_metadata.metadata) == ["a", "b", "c", "d", "e", "f"]
