from pathlib import Path
import platform
import typing as ty
import pytest
from fileformats.core import hook, MockMixin, FileSet
from fileformats.testing import Foo


def test_sample():
    test_inst = Foo.sample()
    assert test_inst.fspath.exists()
    assert test_inst.fspath.suffix == ".foo"


def test_mock():
    mock = Foo.mock()
    if platform.system() == "Windows":
        expected = Path("\\mock\\foo.foo")
    else:
        expected = Path("/mock/foo.foo")
    assert mock.fspath == expected
    assert not mock.fspath.exists()
    assert isinstance(mock, MockMixin)


class Woo(FileSet):
    @hook.extra
    def test_hook(self, a: int, b: float, c: ty.Optional[str] = None) -> float:
        raise NotImplementedError


def test_hook_signature_no_default():
    @Woo.test_hook.register
    def woo_test_hook(woo: Woo, a: int, b: float) -> float:
        pass


def test_hook_signature1():

    with pytest.raises(TypeError, match="missing required argument"):

        @Woo.test_hook.register
        def woo_test_hook(woo: Woo, a: int) -> float:
            pass


def test_hook_signature2():

    with pytest.raises(TypeError, match="name of parameter"):

        @Woo.test_hook.register
        def woo_test_hook(woo: Woo, a: int, d: str) -> float:
            pass


def test_hook_signature3():

    with pytest.raises(TypeError, match="found additional argument"):

        @Woo.test_hook.register
        def woo_test_hook(
            woo: Woo, a: int, b: float, c: ty.Optional[str], d: int
        ) -> float:
            pass


def test_hook_signature4():

    with pytest.raises(TypeError, match="return type"):

        @Woo.test_hook.register
        def woo_test_hook(woo: Woo, a: int, b: str) -> int:
            pass
