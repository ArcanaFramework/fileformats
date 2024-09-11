import sys
import typing as ty
from pathlib import Path
import time
from threading import RLock
import fileformats.core


PropReturn = ty.TypeVar("PropReturn")


__all__ = ["mtime_cached_property", "classproperty"]


class mtime_cached_property:
    """A property that is cached until the mtimes of the files in the fileset are changed"""

    def __init__(self, func: ty.Callable[..., ty.Any]):
        self.func = func
        self.__doc__ = func.__doc__
        self.lock = RLock()
        self._cache_name = f"_{func.__name__}_mtime_cache"

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
                if (
                    instance.mtimes == mtimes
                    and enough_time_has_elapsed_given_mtime_resolution(mtimes)
                ):
                    return value
            value = self.func(instance)
            instance.__dict__[self._cache_name] = (instance.mtimes, value)
        return value


def classproperty(meth: ty.Callable[..., PropReturn]) -> PropReturn:
    """Access a @classmethod like a @property."""
    # mypy doesn't understand class properties yet: https://github.com/python/mypy/issues/2563
    return classmethod(property(meth))  # type: ignore


if sys.version_info[:2] < (3, 9):

    class classproperty(object):  # type: ignore[no-redef]  # noqa
        def __init__(self, f: ty.Callable[[ty.Type[ty.Any]], ty.Any]):
            self.f = f

        def __get__(self, obj: ty.Any, owner: ty.Any) -> ty.Any:
            return self.f(owner)


def enough_time_has_elapsed_given_mtime_resolution(
    mtimes: ty.Iterable[ty.Tuple[Path, int]], current_time: ty.Optional[int] = None
) -> bool:
    """Determines whether enough time has elapsed since the the last of the cached mtimes
    to be sure that changes in mtimes will be detected given the resolution of the mtimes
    on the file system. For example, on systems with a mtime resolution of a second,
    a change in mtime may not be detected if the cache is re-read within a second and
    the file is modified in the intervening period (probably only likely during tests).
    So this function guesses the resolution of the mtimes by the
    minimum number of trailing zeros in the mtimes and then checks if enough time has
    passed to be sure that any changes in mtimes will be detected.

    This may result in false negatives for systems with low mtime resolutions, but
    this will just result in (presumably minor) performance hit via unnecessary cache
    invalidations.

    Parameters
    ----------
    mtimes : Iterable[tuple[Path, int]]
        the path-mtime pairs in nanoseconds to guess the resolution of

    Returns
    -------
    bool
        whether enough time has elapsed since the lagiven the guessed resolution of the mtimes
    """
    max_mtime = 0
    LARGE_INT = 10**18  # Larger than any reasonable mtime resolution but still int64
    guessed_mtime_res = LARGE_INT
    for _, mtime in mtimes:
        if mtime > max_mtime:
            max_mtime = mtime
        res = 1
        mt = mtime
        while mt % 10 == 0:
            mt //= 10
            res *= 10
        if res < guessed_mtime_res:
            guessed_mtime_res = res
    if guessed_mtime_res == LARGE_INT:
        raise ValueError("No mtimes provided")
    if current_time is None:
        current_time = time.time_ns()
    elapsed_time = current_time - max_mtime
    return elapsed_time > guessed_mtime_res
