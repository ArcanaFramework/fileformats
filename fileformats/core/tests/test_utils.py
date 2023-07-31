from pathlib import Path
import os.path
import random
import shutil
import typing as ty
import time
import pytest
from fileformats.core import FileSet, mark
from fileformats.generic import File, Directory, FsObject
from fileformats.core.mixin import WithSeparateHeader
from fileformats.core.utils import (
    find_matching,
    to_mime,
    from_mime,
)
from fileformats.core.exceptions import FileFormatsError
from fileformats.testing import Foo, Bar
import fileformats.text
from conftest import write_test_file


class Mario(File):
    ext = ".mario"


class Luigi(WithSeparateHeader, File):
    ext = ".luigi"
    header_type = Mario


class Bowser(Directory):
    content_types = (Mario,)


@pytest.fixture
def bowser_dir(work_dir):
    bowser_dir = work_dir / "bowser"
    bowser_dir.mkdir()
    for i in range(5):
        bar_fspath = bowser_dir / f"{i}.mario"
        write_test_file(bar_fspath)
    return Bowser(bowser_dir)


@pytest.fixture
def luigi_file(work_dir):
    luigi_fspath = work_dir / "x.luigi"
    write_test_file(luigi_fspath)
    bar_fspath = work_dir / "y.mario"
    write_test_file(bar_fspath)
    return Luigi([luigi_fspath, bar_fspath])


@pytest.fixture(params=["luigi", "bowser"])
def fsobject(luigi_file, bowser_dir, request):
    if request.param == "luigi":
        return luigi_file
    elif request.param == "bowser":
        return bowser_dir
    else:
        assert False


@pytest.fixture
def dest_dir(work_dir):
    dest_dir = work_dir / "new-dir"
    dest_dir.mkdir()
    return dest_dir


def test_copy(fsobject: FsObject, dest_dir: Path):
    cpy = fsobject.copy(dest_dir)
    assert all(p.parent == dest_dir for p in cpy.fspaths)
    assert set(p.name for p in cpy.fspaths) == set(p.name for p in fsobject.fspaths)
    assert cpy.hash() == fsobject.hash()


def test_copy_symlink(fsobject: FsObject, dest_dir: Path):
    cpy = fsobject.copy(dest_dir, mode=File.CopyMode.symlink)
    assert all(p.parent == dest_dir for p in cpy.fspaths)
    assert set(p.name for p in cpy.fspaths) == set(p.name for p in fsobject.fspaths)
    assert all(p.is_symlink() for p in cpy.fspaths)
    assert cpy.hash() == fsobject.hash()


def test_copy_symlink_with_fallback(fsobject: FsObject, dest_dir: Path):
    "Simulate source object on CIFS share, should be copied not symlinked"
    cpy = fsobject.copy(
        dest_dir,
        mode=File.CopyMode.link_or_copy,
        supported_modes=File.CopyMode.hardlink_or_copy,
    )
    assert all(p.parent == dest_dir for p in cpy.fspaths)
    assert set(p.name for p in cpy.fspaths) == set(p.name for p in fsobject.fspaths)
    assert not any(p.is_symlink() for p in cpy.fspaths)
    assert cpy.hash() == fsobject.hash()


def test_copy_symlink_with_unrequired_fallback(fsobject: FsObject, dest_dir: Path):
    "Simulate source object not on CIFS share, should be symlinked not copied"
    cpy = fsobject.copy(
        dest_dir, mode=File.CopyMode.link_or_copy, supported_modes=File.CopyMode.link
    )
    assert all(p.parent == dest_dir for p in cpy.fspaths)
    assert set(p.name for p in cpy.fspaths) == set(p.name for p in fsobject.fspaths)
    assert all(p.is_symlink() for p in cpy.fspaths)
    assert cpy.hash() == fsobject.hash()


def test_copy_hardlink(fsobject: FsObject, dest_dir: Path):
    cpy = fsobject.copy(dest_dir, mode=File.CopyMode.symlink)
    assert all(p.parent == dest_dir for p in cpy.fspaths)
    assert set(p.name for p in cpy.fspaths) == set(p.name for p in fsobject.fspaths)
    assert all(
        os.path.samefile(c, o)
        for c, o in zip(sorted(cpy.fspaths), sorted(fsobject.fspaths))
        if o.is_file()
    )
    assert cpy.hash() == fsobject.hash()


def test_copy_collation_same_name(work_dir: Path, dest_dir: Path):
    a = work_dir / "a" / "file.txt"
    b = work_dir / "b" / "file.txt"
    c = work_dir / "c" / "d" / "file.txt"
    fspaths = (a, b, c)

    for x in fspaths:
        x.parent.mkdir(parents=True)
        Path.touch(x)

    fileset = FileSet(fspaths)

    with pytest.raises(
        FileFormatsError,
        match="as there are duplicate filenames",
    ):
        fileset.copy(dest_dir=dest_dir, collation="siblings")
    cpy = fileset.copy(dest_dir=dest_dir, collation="any")
    assert sorted(cpy.relative_fspaths) == sorted(fileset.relative_fspaths)
    assert cpy.parent == dest_dir


def test_copy_collation_same_ext(work_dir: Path, dest_dir: Path):
    a = work_dir / "a" / "filea.txt"
    b = work_dir / "b" / "fileb.txt"
    c = work_dir / "c" / "d" / "filec.txt"
    fspaths = (a, b, c)

    for x in fspaths:
        x.parent.mkdir(parents=True)
        Path.touch(x)

    fileset = FileSet(fspaths)

    with pytest.raises(
        FileFormatsError,
        match="as there are duplicate extensions",
    ):
        fileset.copy(dest_dir=dest_dir, collation="adjacent")
    cpy = fileset.copy(dest_dir=dest_dir, collation="siblings")
    assert sorted(p.name for p in cpy.fspaths) == sorted(
        p.name for p in fileset.fspaths
    )
    assert all(p.parent == dest_dir for p in cpy.fspaths)


def test_copy_collation_diff_ext(work_dir: Path, dest_dir: Path):
    a = work_dir / "a" / "filea.x"
    b = work_dir / "b" / "fileb.y"
    c = work_dir / "c" / "d" / "filec.z"
    fspaths = (a, b, c)

    for x in fspaths:
        x.parent.mkdir(parents=True)
        Path.touch(x)

    fileset = FileSet(fspaths)

    cpy = fileset.copy(dest_dir=dest_dir, collation="adjacent")
    assert all(p.parent == dest_dir for p in cpy.fspaths)
    assert all(p.stem == "filea" for p in cpy.fspaths)


def test_copy_collation_stem(work_dir: Path, dest_dir: Path):
    a = work_dir / "a" / "filea.x"
    b = work_dir / "b" / "fileb.y"
    c = work_dir / "c" / "d" / "filec.z"
    fspaths = (a, b, c)

    for x in fspaths:
        x.parent.mkdir(parents=True)
        Path.touch(x)

    fileset = FileSet(fspaths)

    cpy = fileset.copy(dest_dir=dest_dir, collation="adjacent", new_stem="newfile")
    assert all(p.parent == dest_dir for p in cpy.fspaths)
    assert all(p.stem == "newfile" for p in cpy.fspaths)


def test_copy_collation_with_stem_not_adjacent(luigi_file: Luigi, dest_dir):
    with pytest.raises(
        FileFormatsError, match="when collation is not set to 'adjacent'"
    ):
        luigi_file.copy(dest_dir, collation="any", new_stem="new")


def test_copy_collation_leave_diff_dir(work_dir: Path, dest_dir: Path):
    a = work_dir / "a" / "file.x"
    b = work_dir / "b" / "file.y"
    c = work_dir / "c" / "file.z"
    fspaths = (a, b, c)

    for x in fspaths:
        x.parent.mkdir(parents=True)
        Path.touch(x)

    fileset = FileSet(fspaths)

    with pytest.raises(
        FileFormatsError,
        match="using leave mode as it is not supported by the any given the collation specification",
    ):
        fileset.copy(dest_dir=dest_dir, mode="leave", collation="siblings")

    with pytest.raises(
        FileFormatsError,
        match="using leave mode as it is not supported by the any given the collation specification",
    ):
        fileset.copy(dest_dir=dest_dir, mode="leave", collation="adjacent")


def test_copy_ext(work_dir):
    assert (
        File.copy_ext(
            work_dir / "x.luigi.mario",
            work_dir / "y",
            decomposition_mode=FileSet.ExtensionDecomposition.none,
        )
        == work_dir / "y"
    )
    assert (
        File.copy_ext(
            work_dir / "x.luigi.mario",
            work_dir / "y",
            decomposition_mode=FileSet.ExtensionDecomposition.single,
        )
        == work_dir / "y.mario"
    )
    assert (
        File.copy_ext(
            work_dir / "x.luigi.mario",
            work_dir / "y",
            decomposition_mode=FileSet.ExtensionDecomposition.multiple,
        )
        == work_dir / "y.luigi.mario"
    )
    assert (
        Mario.copy_ext(work_dir / "x.luigi.mario", work_dir / "y")
        == work_dir / "y.mario"
    )


def test_decompose_fspaths(work_dir):
    class LuigiMario(File):
        ext = ".luigi.mario"

    class DoubleMario(FileSet):
        @mark.required
        @property
        def bar(self):
            return Mario(self.select_by_ext(Mario))

        @mark.required
        @property
        def luigi_bar(self):
            return LuigiMario(self.select_by_ext(LuigiMario))

    fspath = work_dir / "file.luigi.mario"
    Path.touch(fspath)
    double_bar = DoubleMario(fspath)

    with pytest.warns(match="whereas it is also interpreted as a"):
        decomposed = double_bar.decomposed_fspaths()

    assert decomposed == [(work_dir, "file.luigi", ".mario")]


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


def test_hash(tmp_path: Path):
    file_1 = tmp_path / "file_1.txt"
    file_2 = tmp_path / "file_2.txt"
    file_1.write_text("hello")
    file_2.write_text("hello")

    assert File(file_1).hash() == File(file_2).hash()


def test_hash_function_files_mismatch(tmp_path: Path):
    file_1 = tmp_path / "file_1.txt"
    file_2 = tmp_path / "file_2.txt"
    file_1.write_text("hello")
    file_2.write_text("hi")

    assert File(file_1).hash() != File(file_2).hash()


def test_hash_dir(tmp_path: Path):
    dir1 = tmp_path / "luigi"
    dir2 = tmp_path / "bar"
    for d in (dir1, dir2):
        d.mkdir()
        for i in range(3):
            f = d / f"{i}.txt"
            f.write_text(str(i))

    assert Directory(dir1).hash() == Directory(dir2).hash()


def test_hash_nested_dir(tmp_path: Path):
    dpath = tmp_path / "dir"
    dpath.mkdir()
    hidden = dpath / ".hidden"
    nested = dpath / "nested"
    hidden.mkdir()
    nested.mkdir()
    file_1 = dpath / "file_1.txt"
    file_2 = hidden / "file_2.txt"
    file_3 = nested / ".file_3.txt"
    file_4 = nested / "file_4.txt"

    for fx in [file_1, file_2, file_3, file_4]:
        fx.write_text(str(random.randint(0, 1000)))

    nested_dir = Directory(dpath)

    orig_hash = nested_dir.hash()

    nohidden_hash = nested_dir.hash(ignore_hidden_dirs=True, ignore_hidden_files=True)
    nohiddendirs_hash = nested_dir.hash(ignore_hidden_dirs=True)
    nohiddenfiles_hash = nested_dir.hash(ignore_hidden_files=True)

    assert orig_hash != nohidden_hash
    assert orig_hash != nohiddendirs_hash
    assert orig_hash != nohiddenfiles_hash

    os.remove(file_3)
    assert nested_dir.hash() == nohiddenfiles_hash
    shutil.rmtree(hidden)
    assert nested_dir.hash() == nohidden_hash


def test_hash_mtime(tmp_path: Path):
    file_1 = tmp_path / "file_1.txt"
    file_2 = tmp_path / "file_2.txt"
    file_1.write_text("hello")
    file_2.write_text("hello")

    orig_hash = File(file_1).hash(mtime=True)

    assert File(file_1).hash(mtime=True) == orig_hash
    assert File(file_2).hash(mtime=True) != orig_hash

    time.sleep(1)
    Path.touch(file_1)
    assert File(file_1).hash(mtime=True) != orig_hash


def test_hash_files(fsobject: FsObject, work_dir: Path, dest_dir: Path):
    file_hashes = fsobject.hash_files(relative_to=work_dir)
    assert sorted(Path(p) for p in file_hashes) == sorted(
        p.relative_to(work_dir) for p in fsobject.all_file_paths
    )
    cpy = fsobject.copy(dest_dir)
    assert cpy.hash_files() == fsobject.hash_files()


def test_to_from_mime_roundtrip():
    mime_str = to_mime(Foo)
    assert isinstance(mime_str, str)
    assert from_mime(mime_str) == Foo


def test_to_from_list_mime_roundtrip():
    mime_str = to_mime(ty.List[Foo])
    assert isinstance(mime_str, str)
    assert from_mime(mime_str) == ty.List[Foo]


def test_to_from_union_mime_roundtrip():
    mime_str = to_mime(ty.Union[Foo, Bar])
    assert isinstance(mime_str, str)
    assert from_mime(mime_str) == ty.Union[Foo, Bar]


def test_to_from_list_union_mime_roundtrip():
    mime_str = to_mime(ty.List[ty.Union[Foo, Bar]])
    assert isinstance(mime_str, str)
    assert from_mime(mime_str) == ty.List[ty.Union[Foo, Bar]]


def test_official_mime_fail():
    with pytest.raises(TypeError, match="as it is not a proper file-type"):
        to_mime(ty.List[Foo], official=True)
