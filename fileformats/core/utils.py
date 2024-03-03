import importlib
from pathlib import Path
import inspect
import typing as ty
import urllib.request
import urllib.error
import os
import logging
import pkgutil
from contextlib import contextmanager
import fileformats.core


logger = logging.getLogger("fileformats")


_excluded_subpackages = set(["core", "testing", "serialization", "archive", "document"])


def include_testing_package(flag: bool = True):
    """Include testing package in list of sub-packages. Typically set in conftest.py
    or similar when setting up unittesting. Must be set globally before any methods are
    called within the package as member classes are cached.

    Parameters
    ----------
    flag : bool
        whether to include the testing package or not
    """
    global _excluded_subpackages
    if flag:
        _excluded_subpackages.remove("testing")
    else:
        _excluded_subpackages.add("testing")


def subpackages(exclude: ty.Sequence[str] = _excluded_subpackages):
    """Iterates over all subpackages within the fileformats namespace

    Parameters
    ----------
    exclude : ty.Sequence[str], optional
        whether to include the testing subpackage, by default ["core", "testing"]

    Yields
    ------
    module
        all modules within the package
    """
    for mod_info in pkgutil.iter_modules(
        fileformats.__path__, prefix=fileformats.__package__ + "."
    ):
        if mod_info.name.split(".")[-1] in exclude:
            continue
        yield importlib.import_module(mod_info.name)


@contextmanager
def set_cwd(path: Path):
    """Sets the current working directory to `path` and back to original
    working directory on exit

    Parameters
    ----------
    path : str
        The file system path to set as the current working directory
    """
    pwd = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(pwd)


def fspaths_converter(
    fspaths: ty.Union[
        ty.Iterable[ty.Union[str, os.PathLike, bytes]],
        str,
        os.PathLike,
        bytes,
        "fileformats.core.FileSet",
    ]
):
    """Ensures fs-paths are a set of pathlib.Path"""
    import fileformats.core

    if isinstance(fspaths, fileformats.core.FileSet):
        fspaths = fspaths.fspaths
    elif isinstance(fspaths, (str, os.PathLike, bytes)):
        fspaths = [fspaths]
    return frozenset(Path(p).absolute() for p in fspaths)


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


def add_exc_note(e, note):
    """Adds a note to an exception in a Python <3.11 compatible way

    Parameters
    ----------
    e : Exception
        the exception to add the note to
    note : str
        the note to add

    Returns
    -------
    Exception
        returns the exception again
    """
    if hasattr(e, "add_note"):
        e.add_note(note)
    else:
        e.args = (e.args[0] + "\n" + note,)
    return e


def describe_task(task):
    """Returns the name of a Pydra task and where it was defined for debugging purposes

    Parameters
    ----------
    task : pydra.engine.core.TaskBase
        the task to describe
    """
    from fileformats.core.converter import ConverterWrapper

    if isinstance(task, ConverterWrapper):
        task = task.task_spec
    if inspect.isfunction(task):
        import cloudpickle

        task = cloudpickle.loads(task().inputs._func)
    src_file = inspect.getsourcefile(task)
    src_line = inspect.getsourcelines(task)[-1]
    return f"{task} (defined at line {src_line} of {src_file})"


def matching_source(task1, task2) -> bool:
    """Checks to see if the tasks share the same source code but are just getting reimported
    for some unknown reason"""
    return (
        inspect.getsourcefile(task1) == inspect.getsourcefile(task2)
        and inspect.getsourcelines(task1)[-1] == inspect.getsourcelines(task2)[-1]
    )


def check_package_exists_on_pypi(package_name: str, timeout: int = 5) -> bool:
    """Check if a package exists on PyPI

    Parameters
    ----------
    package_name : str
        the name of the package to check for

    Returns
    -------
    bool
        whether the package exists on PyPI or not
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        urllib.request.urlopen(url, timeout=timeout)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        else:
            raise
    return True


class ExtrasModule:
    def __init__(self, imported: bool, pkg: str, pypi: str):
        self.imported = imported
        self.pkg = pkg
        self.pypi = pypi


def import_extras_module(klass: type) -> ExtrasModule:
    """Attempt to load extras module corresponding to the provided class's module

    Parameters
    ----------
    klass : ty.Type
        the class to load the extras module for

    Returns
    -------
    imported : bool
        whether the module was imported or not
    sub_pkg : str
        the name of the sub-package that was attempted to be loaded
    """
    from .identification import IANA_MIME_TYPE_REGISTRIES

    # Check for Mock class
    try:
        klass = klass.TRUE_CLASS
    except AttributeError:
        pass
    pkg_parts = klass.__module__.split(".")
    if pkg_parts[0] != "fileformats":
        logger.debug(
            "There is no 'extras' module for classes not within the 'fileformats' package, "
            "not %s in %s",
            klass.__name__,
            klass.__module__,
        )
        return True, None, None
    sub_pkg = pkg_parts[1]
    extras_pkg = "fileformats.extras." + sub_pkg
    if sub_pkg in IANA_MIME_TYPE_REGISTRIES + ["testing"]:
        extras_pypi = "fileformats-extras"
    else:
        extras_pypi = f"fileformats-{sub_pkg.replace('_', '-')}-extras"
    try:
        importlib.import_module(extras_pkg)
    except ModuleNotFoundError as e:
        if str(e) != f"No module named '{extras_pkg}'":
            raise
        extras_imported = False
    else:
        extras_imported = True
    return ExtrasModule(extras_imported, extras_pkg, extras_pypi)
