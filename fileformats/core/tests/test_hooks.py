from pathlib import Path
import platform
import typing as ty
import pytest
from fileformats.core import extra, MockMixin, FileSet, extra_implementation
from fileformats.testing import Foo


def test_sample():
    test_inst = Foo.sample()
    assert test_inst.fspath.exists()
    assert test_inst.fspath.suffix == ".foo"


def test_mock():
    mock = Foo.mock()
    if platform.system() == "Windows":
        expected = Path(f"{Path().cwd().drive}\\mock\\foo.foo")
    else:
        expected = Path("/mock/foo.foo")
    assert mock.fspath == expected
    assert not mock.fspath.exists()
    assert isinstance(mock, MockMixin)


class Woo(FileSet):
    @extra
    def test_extra(self, a: int, b: float, c: ty.Optional[str] = None) -> float:
        raise NotImplementedError


def test_extra_signature_no_default():
    extra_implementation(Woo.test_extra)

    def woo_test_extra(woo: Woo, a: int, b: float) -> float:
        pass


def test_extra_signature1():

    with pytest.raises(TypeError, match="missing required argument"):

        extra_implementation(Woo.test_extra)

        def woo_test_extra(woo: Woo, a: int) -> float:
            pass


def test_extra_signature2():

    with pytest.raises(TypeError, match="name of parameter"):

        extra_implementation(Woo.test_extra)

        def woo_test_extra(woo: Woo, a: int, d: str) -> float:
            pass


def test_extra_signature3():

    with pytest.raises(TypeError, match="found additional argument"):

        extra_implementation(Woo.test_extra)

        def woo_test_extra(
            woo: Woo, a: int, b: float, c: ty.Optional[str], d: int
        ) -> float:
            pass


def test_extra_signature4():

    with pytest.raises(TypeError, match="return type"):

        extra_implementation(Woo.test_extra)

        def woo_test_extra(woo: Woo, a: int, b: str) -> int:
            pass
