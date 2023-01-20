import pytest
from fileformats.generic import File, Directory
from fileformats.core.exceptions import FormatMismatchError
from fileformats.core.mixin import WithSideCar
from conftest import write_test_file


def test_generic_file(work_dir):

    fspath = work_dir / "test.txt"
    write_test_file(fspath)
    file = File(fspath)
    assert file.fspath == fspath
    assert str(file) == str(fspath)


def test_generic_file_fail(work_dir):

    fspath = work_dir / "test-dir"
    fspath.mkdir()
    with pytest.raises(FormatMismatchError):
        File(fspath)


def test_generic_dir(work_dir):

    fspath = work_dir / "test-dir"
    fspath.mkdir()
    d = Directory(fspath)
    assert d.fspath == fspath
    assert str(d) == str(fspath)


def test_generic_dir_fail(work_dir):

    fspath = work_dir / "test.txt"
    write_test_file(fspath)
    with pytest.raises(FormatMismatchError):
        Directory(fspath)


def test_dynamic_dir(work_dir):

    fspath = work_dir / "test-dir"
    write_test_file(fspath / "test.foo")
    assert Directory[TestFile].matches(fspath)


def test_dynamic_dir_fail(work_dir):

    fspath = work_dir / "test-dir"
    write_test_file(fspath / "test.bad")
    assert not Directory[TestFile].matches(fspath)


class TestFile(File):

    ext = ".foo"


def test_file_ext(work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    assert TestFile.matches(fspath)


def test_file_ext_fail(work_dir):

    fspath = work_dir / "test.bad"
    write_test_file(fspath)
    assert not TestFile.matches(fspath)


def test_single_of_double_ext(work_dir):

    fspath = work_dir / "test.bar.foo"
    write_test_file(fspath)
    assert TestFile.matches(fspath)


def test_file_cast(work_dir):

    fspath = work_dir / "test.foo"
    write_test_file(fspath)
    file = TestFile(fspath)
    assert File(file).fspath == fspath


class TestDir(Directory):

    content_types = (TestFile,)


def test_dir_contents(work_dir):

    fspath = work_dir / "test-dir"
    write_test_file(fspath / "test.foo")
    write_test_file(fspath / "test2.foo")
    write_test_file(fspath / "text.txt")
    assert TestDir.matches(fspath)


def test_dir_contents_fail(work_dir):

    fspath = work_dir / "test-dir"
    write_test_file(fspath / "test.bad")
    write_test_file(fspath / "test.zip")
    write_test_file(fspath / "text.txt")
    assert not TestDir.matches(fspath)


class DoubleExtFileFormat(File):

    ext = ".foo.bar"


def test_double_ext(work_dir):
    fspath = work_dir / "test.foo.bar"
    write_test_file(fspath)
    assert DoubleExtFileFormat.matches(fspath)


def test_double_ext_fail(work_dir):
    fspath = work_dir / "test.foo.bad"
    write_test_file(fspath)
    assert not DoubleExtFileFormat.matches(fspath)


class NestedDirFormat(Directory):

    content_types = (TestFile, DoubleExtFileFormat, TestDir)


def test_nested_directories(work_dir):

    fspath = work_dir / "test-dir"
    write_test_file(fspath / "test.foo")
    write_test_file(fspath / "text.ignored")
    write_test_file(fspath / "text.foo.bar")
    write_test_file(fspath / "nested_dir" / "test.foo")
    write_test_file(fspath / "nested_dir" / "test.ignored")
    assert NestedDirFormat.matches(fspath)


def test_nested_directories_fail(work_dir):

    fspath = work_dir / "test-dir"
    write_test_file(fspath / "test.foo")
    write_test_file(fspath / "text.foo.bar")
    write_test_file(fspath / "nested_dir" / "test.bad")
    write_test_file(fspath / "nested_dir" / "test.ignored")
    assert not NestedDirFormat.matches(fspath)


def test_nested_directories_fail2(work_dir):

    fspath = work_dir / "test-dir"
    write_test_file(fspath / "test.foo")
    write_test_file(fspath / "text.foo.bad")
    write_test_file(fspath / "nested_dir" / "test.foo")
    write_test_file(fspath / "nested_dir" / "test.ignored")
    assert not NestedDirFormat.matches(fspath)


# class FileWithSideCar(File):

#     ext = ".foo"

#     @mark.required
#     @property
#     def bar(self):
#         return self.select_by_ext(".bar")


# def test_side_car(work_dir):
#     fspath = work_dir / "test.foo"
#     write_test_file(fspath)
#     bar_fspath = work_dir / "test.bar"
#     write_test_file(bar_fspath)
#     file = FileWithSideCar([fspath, bar_fspath])
#     assert file.bar == bar_fspath


# def test_side_car2(work_dir):
#     fspath = work_dir / "test.foo"
#     write_test_file(fspath)
#     bar_fspath = work_dir / "whoopwhoop.bar"
#     write_test_file(bar_fspath)
#     file = FileWithSideCar([fspath, bar_fspath])
#     assert file.fspath == fspath
#     assert file.bar == bar_fspath


# def test_side_car_from_primary(work_dir):
#     fspath = work_dir / "test.foo"
#     write_test_file(fspath)
#     bar_fspath = work_dir / "test.bar"
#     write_test_file(bar_fspath)
#     file = FileWithSideCar(fspath)
#     assert file.fspath == fspath
#     assert file.bar == bar_fspath


# def test_side_car_fail(work_dir):
#     fspath = work_dir / "test.foo"
#     write_test_file(fspath)
#     assert not FileWithSideCar.matches(fspath)


# def test_side_car_fail2(work_dir):
#     fspath = work_dir / "test.foo"
#     write_test_file(fspath)
#     fspath = work_dir / "test.bad"
#     write_test_file(fspath)
#     assert not FileWithSideCar.matches(fspath)


class Bar(File):

    ext = ".bar"


class FooWithSideCar(WithSideCar, TestFile):

    side_car_type = Bar


class DirContainingSideCars(Directory):

    content_types = (FooWithSideCar,)


def test_dir_containing_side_cars(work_dir):

    fspath = work_dir / "test-dir"
    write_test_file(fspath / "test.foo")
    write_test_file(fspath / "test.bar")
    write_test_file(fspath / "text.txt")
    assert DirContainingSideCars.matches(fspath)


def test_dir_containing_side_cars_fail(work_dir):

    fspath = work_dir / "test-dir"
    write_test_file(fspath / "test.foo")
    write_test_file(fspath / "diff-name.bar")
    assert not DirContainingSideCars.matches(fspath)
