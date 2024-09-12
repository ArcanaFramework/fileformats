from collections import Counter
import itertools
import typing as ty
import pytest
from fileformats.core import (
    find_matching,
    to_mime,
    from_mime,
    from_paths,
    FileSet,
)
from fileformats.core.exceptions import FormatRecognitionError
from fileformats.testing import Foo, Bar
from fileformats.application import Json, Yaml, Zip
from fileformats.text import Plain, TextFile
import fileformats.text


def test_format_detection(work_dir):
    text_file = work_dir / "text.txt"

    with open(text_file, "w") as f:
        f.write("sample text")

    detected = find_matching(text_file, standard_only=True)
    assert sorted(detected, key=lambda f: f.mime_like) == [
        fileformats.text.Prs_Fallenstein_Rst,
        fileformats.text.Prs_Prop_Logic,
        fileformats.text.TextFile,
    ]


def test_to_from_mime_roundtrip():
    mime_str = to_mime(Foo, official=False)
    assert isinstance(mime_str, str)
    assert from_mime(mime_str) == Foo


def test_to_from_list_mime_roundtrip():
    mime_str = to_mime(ty.List[Foo], official=False)
    assert isinstance(mime_str, str)
    assert from_mime(mime_str) == ty.List[Foo]


def test_to_from_union_mime_roundtrip():
    mime_str = to_mime(ty.Union[Foo, Bar], official=False)
    assert isinstance(mime_str, str)
    assert from_mime(mime_str) == ty.Union[Foo, Bar]


def test_to_from_list_union_mime_roundtrip():
    mime_str = to_mime(ty.List[ty.Union[Foo, Bar]], official=False)
    assert isinstance(mime_str, str)
    assert from_mime(mime_str) == ty.List[ty.Union[Foo, Bar]]


def test_official_mime_fail():
    with pytest.raises(TypeError, match="as it is not a proper file-type"):
        to_mime(ty.List[Foo], official=True)


def test_repr():
    for frmt in FileSet.all_formats:
        assert repr(frmt.mock("/a/path")).startswith(f"{frmt.__name__}(")


def test_from_paths(tmp_path):
    filesets = []
    filesets.append(Json.sample(tmp_path, seed=1))
    filesets.append(Json.sample(tmp_path, seed=2))
    filesets.append(Json.sample(tmp_path, seed=3))
    filesets.append(Yaml.sample(tmp_path, seed=1))
    filesets.append(Yaml.sample(tmp_path, seed=2))
    filesets.append(Zip.sample(tmp_path))
    filesets.append(Foo.sample(tmp_path, seed=1))
    filesets.append(Foo.sample(tmp_path, seed=2))
    filesets.append(Foo.sample(tmp_path, seed=3))
    filesets.append(Bar.sample(tmp_path))
    filesets.append(TextFile.sample(tmp_path))

    fspaths = list(itertools.chain(*(f.fspaths for f in filesets)))

    detected = from_paths(fspaths, Json, Yaml, Zip, Foo, Bar, TextFile)

    assert set(detected) == set(filesets)

    count = Counter(type(f) for f in detected)

    assert count[Json] == 3
    assert count[Zip] == 1
    assert count[Yaml] == 2
    assert count[Foo] == 3
    assert count[Bar] == 1
    assert count[TextFile] == 1

    # redetect, but use a plain text file instead of TextFile
    detected = from_paths(fspaths, Json, Yaml, Zip, Foo, Bar, Plain)

    count = Counter(type(f) for f in detected)

    assert count[Plain] == 1

    with pytest.raises(
        FormatRecognitionError, match="were not recognised by any of the candidate"
    ):
        from_paths(fspaths, Json, Yaml, Zip, Foo, Bar)

    from_paths(fspaths, Json, Yaml, Zip, Foo, Bar, ignore=r".*\.txt")
