from pathlib import Path
import os.path
import random
import shutil
import pytest
from fileformats.generic import File, Directory, FsObject
from fileformats.core.mixin import WithSeparateHeader
from fileformats.core.utils import (
    find_matching,
    MissingExtendedDependency,
)
from fileformats.core.exceptions import MissingExtendedDepenciesError
import fileformats.text
import fileformats.numeric
from conftest import write_test_file


class Bar(File):
    ext = ".bar"


class Foo(WithSeparateHeader, File):
    ext = ".foo"
    header_type = Bar


class Baz(Directory):
    content_types = (Bar,)


@pytest.fixture
def baz_dir(work_dir):
    baz_dir = work_dir / "baz"
    baz_dir.mkdir()
    for i in range(5):
        bar_fspath = baz_dir / f"{i}.bar"
        write_test_file(bar_fspath)
    return Baz(baz_dir)


@pytest.fixture
def foo_file(work_dir):
    foo_fspath = work_dir / "x.foo"
    write_test_file(foo_fspath)
    bar_fspath = work_dir / "y.bar"
    write_test_file(bar_fspath)
    return Foo([foo_fspath, bar_fspath])


@pytest.fixture(params=["foo", "baz"])
def fsobject(foo_file, baz_dir, request):
    if request.param == "foo":
        return foo_file
    elif request.param == "baz":
        return baz_dir
    else:
        assert False


@pytest.fixture
def dest_dir(work_dir):
    dest_dir = work_dir / "new-dir"
    dest_dir.mkdir()
    return dest_dir


def test_copy(fsobject: FsObject, dest_dir: Path):
    cpy = fsobject.copy_to(dest_dir)
    assert all(p.parent == dest_dir for p in cpy.fspaths)
    assert set(p.name for p in cpy.fspaths) == set(p.name for p in fsobject.fspaths)
    assert cpy.hash() == fsobject.hash()


def test_copy_symlink(fsobject: FsObject, dest_dir: Path):
    cpy = fsobject.copy_to(dest_dir, link_type="symbolic")
    assert all(p.parent == dest_dir for p in cpy.fspaths)
    assert set(p.name for p in cpy.fspaths) == set(p.name for p in fsobject.fspaths)
    assert set(p.is_symlink() for p in cpy.fspaths)
    assert cpy.hash() == fsobject.hash()


def test_copy_hardlink(fsobject: FsObject, dest_dir: Path):
    cpy = fsobject.copy_to(dest_dir, link_type="hard")
    assert all(p.parent == dest_dir for p in cpy.fspaths)
    assert set(p.name for p in cpy.fspaths) == set(p.name for p in fsobject.fspaths)
    assert all(
        os.path.samefile(c, o)
        for c, o in zip(sorted(cpy.fspaths), sorted(fsobject.fspaths))
        if o.is_file()
    )
    assert cpy.hash() == fsobject.hash()


def test_copy_with_rename(foo_file, dest_dir):
    cpy = foo_file.copy_to(dest_dir, stem="new")
    assert cpy.fspath.name == "new.foo"
    assert cpy.header.fspath.name == "new.bar"


def test_copy_ext(work_dir):
    assert (
        File.copy_ext(work_dir / "x.foo.bar", work_dir / "y") == work_dir / "y.foo.bar"
    )
    assert Bar.copy_ext(work_dir / "x.foo.bar", work_dir / "y") == work_dir / "y.bar"


def test_format_detection(work_dir):
    text_file = work_dir / "text.txt"

    with open(text_file, "w") as f:
        f.write("sample text")

    detected = find_matching(text_file, standard_only=True)
    assert len(detected) == 1
    assert detected[0] is fileformats.text.Plain


def test_missing_dependency():
    missing_dep = MissingExtendedDependency("missing_dep", "fileformats.image")

    with pytest.raises(MissingExtendedDepenciesError):
        missing_dep.an_attr


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
    dir1 = tmp_path / "foo"
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

    Path.touch(file_1)
    assert File(file_1).hash(mtime=True) != orig_hash
