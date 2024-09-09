import sys
import typing as ty
from threading import RLock

if ty.TYPE_CHECKING:
    import fileformats.core


ReturnType = ty.TypeVar("ReturnType")


class contents_property:
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
            "Cannot use contents_property instance with "
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


PropReturn = ty.TypeVar("PropReturn")


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
