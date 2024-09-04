import importlib
from pathlib import Path
import inspect
import sys
import typing as ty
from types import ModuleType
import urllib.request
import urllib.error
from threading import RLock
import os
import logging
import pkgutil
from contextlib import contextmanager
from .typing import FspathsInputType
import fileformats.core

if ty.TYPE_CHECKING:
    import pydra.engine.core

logger = logging.getLogger("fileformats")


_excluded_subpackages = set(
    ["core", "testing", "serialization", "archive", "document", "conftest"]
)

T = ty.TypeVar("T")


def include_testing_package(flag: bool = True) -> None:
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


def subpackages(
    exclude: ty.Iterable[str] = _excluded_subpackages,
) -> ty.Generator[ModuleType, None, None]:
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
def set_cwd(path: Path) -> ty.Generator[Path, None, None]:
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


def fspaths_converter(fspaths: FspathsInputType) -> ty.FrozenSet[Path]:
    """Ensures fs-paths are a set of pathlib.Path"""
    import fileformats.core

    if isinstance(fspaths, fileformats.core.FileSet):
        fspaths = fspaths.fspaths
    elif isinstance(fspaths, (str, os.PathLike)):
        fspaths = [Path(fspaths)]
    return frozenset(Path(p).absolute() for p in fspaths)


PropReturn = ty.TypeVar("PropReturn")

if sys.version_info[:2] >= (3, 9):

    def classproperty(meth: ty.Callable[..., PropReturn]) -> PropReturn:
        """Access a @classmethod like a @property."""
        # mypy doesn't understand class properties yet: https://github.com/python/mypy/issues/2563
        return classmethod(property(meth))  # type: ignore

else:

    class classproperty(object):
        def __init__(self, f: ty.Callable[[ty.Type[ty.Any]], ty.Any]):
            self.f = f

        def __get__(self, obj: ty.Any, owner: ty.Any) -> ty.Any:
            return self.f(owner)


def add_exc_note(e: Exception, note: str) -> Exception:
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


def describe_task(task: "pydra.engine.task.TaskBase") -> str:
    """Returns the name of a Pydra task and where it was defined for debugging purposes

    Parameters
    ----------
    task : pydra.engine.core.TaskBase
        the task to describe
    """
    from fileformats.core.converter_helpers import ConverterWrapper

    if isinstance(task, ConverterWrapper):
        task = task.task_spec
    if inspect.isfunction(task):
        import cloudpickle

        try:
            task = cloudpickle.loads(task().inputs._func)
        except Exception as e:
            return f"{task} (Failed to load task function: {e})"
    src_file = inspect.getsourcefile(task)
    src_line = inspect.getsourcelines(task)[-1]
    return f"{task} (defined at line {src_line} of {src_file})"


def matching_source(
    task1: ty.Callable[..., ty.Any], task2: ty.Callable[..., ty.Any]
) -> bool:
    """Checks to see if the tasks share the same source code but are just getting reimported
    for some unknown reason"""
    mod1 = inspect.getmodule(task1)
    mod2 = inspect.getmodule(task2)
    assert mod1 and mod2
    return inspect.getsource(mod1) == inspect.getsource(mod2)


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
    def __init__(self, imported: bool, pkg: ty.Optional[str], pypi: ty.Optional[str]):
        self.imported = imported
        self.pkg = pkg
        self.pypi = pypi


def import_extras_module(klass: ty.Type["fileformats.core.DataType"]) -> ExtrasModule:
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
        klass = klass.TRUE_CLASS  # type: ignore
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
        return ExtrasModule(True, None, None)
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


ReturnType = ty.TypeVar("ReturnType")


class mtime_cached_property:
    """A property that is cached until the mtimes of the files in the fileset are changed"""

    def __init__(self, func: ty.Callable[..., ty.Any]):
        self.func = func
        self.__doc__ = func.__doc__
        self.lock = RLock()

    @property
    def _cache_name(self) -> str:
        return f"_{self.func.__name__}_mtime_cache"

    def clear(self, instance: "fileformats.core.FileSet") -> None:
        """Forcibly clear the cache"""
        del instance.__dict__[self._cache_name]

    def __get__(
        self,
        instance: ty.Optional["fileformats.core.FileSet"],
        owner: ty.Optional[ty.Type["fileformats.core.FileSet"]] = None,
    ) -> ty.Any:
        if instance is None:  # if accessing property from class not instance
            return self
        assert isinstance(instance, fileformats.core.FileSet), (
            "Cannot use mtime_cached_property instance with "
            f"{type(instance).__name__!r} object, only FileSet objects."
        )
        try:
            mtimes, value = instance.__dict__[self._cache_name]
        except KeyError:
            pass
        else:
            if instance.mtimes == mtimes:
                return value
        with self.lock:
            # check if another thread filled cache while we awaited lock
            try:
                mtimes, value = instance.__dict__[self._cache_name]
            except KeyError:
                pass
            else:
                if instance.mtimes == mtimes:
                    return value
            value = self.func(instance)
            instance.__dict__[self._cache_name] = (instance.mtimes, value)
        return value
