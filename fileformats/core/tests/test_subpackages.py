from fileformats.core.utils import (
    include_testing_package,
    subpackages,
)


def test_include_testing():
    assert "fileformats.testing" not in [
        p.__name__ for p in subpackages(exclude=("core", "testing"))
    ]
    assert "fileformats.testing" in [p.__name__ for p in subpackages(exclude=("core",))]


def test_include_testing_flag():
    assert "fileformats.testing" in [p.__name__ for p in subpackages()]
    include_testing_package(False)
    try:
        pkgs = list(subpackages())
    finally:
        include_testing_package(True)
    assert "fileformats.testing" not in [p.__name__ for p in pkgs]
    assert "fileformats.testing" in [p.__name__ for p in subpackages()]
