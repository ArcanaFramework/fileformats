from __future__ import annotations
import importlib
import operator
from pathlib import Path
import random
import string
import inspect
import typing as ty
import re
import urllib.request
import urllib.error
import os
import logging
import pkgutil
from contextlib import contextmanager
from fileformats.core.exceptions import (
    FileFormatsError,
    FormatRecognitionError,
)
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


def find_matching(
    fspaths: ty.List[Path],
    candidates: ty.Sequence = None,
    standard_only: bool = False,
    include_generic: bool = False,
    skip_unconstrained: bool = True,
):
    """Detect the corresponding file format from a set of file-system paths

    Parameters
    ----------
    fspaths : list[Path]
        file-system paths to detect the format of
    candidates: sequence[DataType], optional
        the candidates to select from, by default all file formats
    standard_only : bool, optional
        If you only want to return matches from the "standard" IANA types. Only relevant
        if candidates is None, by default False
    skip_unconstrained : bool, optional
        skip formats that aren't constrained by extension, magic number or another check.
        Only relevant if candidates is None
    """
    import fileformats.core.mixin

    fspaths = fspaths_converter(fspaths)
    matches = []
    if candidates is None:
        candidates = fileformats.core.FileSet.all_formats
    for frmt in candidates:
        if skip_unconstrained and frmt.unconstrained:
            continue
        namespace = frmt.namespace
        if (
            frmt.matches(fspaths)
            and (not standard_only or namespace in IANA_MIME_TYPE_REGISTRIES)
            and (include_generic or namespace != "generic")
        ):
            matches.append(frmt)
    return matches


def from_mime(mime_str: str):
    """Resolves a MIME type (or MIME-like) string into the corresponding type

    Parameters
    ----------
    mime_str : str
        the MIME type, or MIME-like (i.e. using the fileformats namespace scheme
        instead of putting all non-standard types into application/*), string to
        resolve

    Returns
    -------
    datatype : type
        the resolved datatype
    """
    if mime_str.endswith(LIST_MIME):
        item_mime = mime_str[: -len(LIST_MIME)]
        if item_mime.startswith("[") and item_mime.endswith("]"):
            item_mime = item_mime[1:-1]
        return ty.List[from_mime(item_mime)]
    if "," in mime_str:
        return ty.Union.__getitem__(tuple(from_mime(t) for t in mime_str.split(",")))
    return fileformats.core.DataType.from_mime(mime_str)


def to_mime(datatype: type, official: bool = True):
    """Returns the mime-type or mime-like (i.e. using fileformats namespaces instead
    of putting all non-standard types in the applications/* registry) string corresponding
    to the given datatype

    Parameters
    ----------
    datatype : type
        the datatype to get the mime string for
    official : bool
        whether to use the official mime-type instead of mime-like

    Returns
    -------
    mime_str : str
        the MIME type string if `iana=True`, or MIME-like (i.e. using the fileformats
        namespace scheme instead of putting all non-standard types into application/*)
        if not
    """
    origin = ty.get_origin(datatype)
    if official and (origin or datatype.namespace == "field"):
        raise TypeError(
            f"Cannot convert {datatype} to official mime-type as it is not a proper "
            'file-type, please use official=False to convert to "mime-like" string instead'
        )
    if origin is list:
        item_mime = to_mime(ty.get_args(datatype)[0], official=official)
        if "," in item_mime:
            item_mime = "[" + item_mime + "]"
        item_mime += LIST_MIME
        return item_mime
    if origin is ty.Union:
        return ",".join(to_mime(t, official=official) for t in ty.get_args(datatype))
    mime = datatype.mime_type if official else datatype.mime_like
    if official:
        mime = datatype.mime_type
    else:
        mime = datatype.mime_like
        try:
            from_mime(mime)
        except FormatRecognitionError as e:
            add_exc_note(
                e,
                (
                    f"Cannot create reversible MIME type for {datatype}. Please ensure "
                    "it is imported into a top-level fileformats namespace package "
                    f"'{datatype.namespace}'"
                ),
            )
            raise e
    return mime


def from_paths(
    fspaths: ty.Iterable[Path],
    *candidates: ty.Tuple[ty.Type[fileformats.core.FileSet]],
    common_ok: bool = False,
    ignore: ty.Optional[str] = None,
    **kwargs,
) -> ty.List[fileformats.core.FileSet]:
    """Given a list of candidate classes (defaults to all installed in alphabetical order),
    instantiates all possible file-set instances from a collection of file-system paths.

    Note that the order in which the candidates are provided is important as the first
    valid match for each path will be returned.

    Parameters
    ----------
    fspaths : ty.Iterable[Path]
        file-system paths to instantiate file-sets from
    *candidates : tuple[fileformats.core.FileSet]
        the file-set classes to instantiate. If none are provided, then all installed
        filesets will be tried in alphabetical order of their "mime-like" representation.
    common_ok : bool
        whether file-system paths can be used as secondary files in multiple file-sets
    ignore: str, optional
        regular expression pattern for file/directory names to ignore if they aren't
        used in any of the returned file-sets. Any remaining file-paths that are not
        matched by this pattern will cause an error to be raised.
    **kwargs: dict[str, Any]
        keyword arguments passed on to the underlying call to FileSet.from_paths

    Returns
    -------
    list[fileformats.core.FileSet]
        the instantiated file-sets
    """
    if candidates:
        # Unwrap any nested tuples into a flat list of file-setclasses
        unwrapped = []

        def unwrap(candidate):
            if ty.get_origin(candidate) is ty.Union:
                for arg in ty.get_args(candidate):
                    unwrapped.extend(unwrap(arg))
            else:
                unwrapped.append(candidate)

        for candidate in candidates:
            unwrap(candidate)
        candidates = unwrapped
        candidates_str = ", ".join(c.mime_like for c in candidates)
    else:
        # Use all installed file-set classes if no candidates are provided, sorted
        # alphabetically to ensure behaviour is consistent between runs
        candidates = sorted(
            fileformats.core.FileSet.subclasses(), key=operator.attrgetter("mime_like")
        )
        candidates_str = "all installed"

    remaining = fspaths
    filesets = []
    for candidate in candidates:
        fsets, remaining = candidate.from_paths(
            remaining, common_ok=common_ok, **kwargs
        )
        filesets.extend(fsets)
    if ignore:
        ignore_re = re.compile(ignore)
        remaining = [p for p in remaining if not ignore_re.match(p.name)]
    if remaining:
        raise FileFormatsError(
            "the following file-system paths were not recognised by any of the "
            f"candidate formats ({candidates_str}):\n"
            + "\n".join(str(p) for p in remaining)
        )
    return filesets


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
        fileformats.core.FileSet,
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


IANA_MIME_TYPE_REGISTRIES = [
    "application",
    "audio",
    "font",
    "image",
    "message",
    "model",
    "multipart",
    "text",
    "video",
]


def to_mime_format_name(format_name: str):
    if "___" in format_name:
        raise FileFormatsError(
            f"Cannot convert name of format class {format_name} to mime string as it "
            "contains triple underscore"
        )
    if format_name.startswith("_"):
        format_name = format_name[1:]
    format_name = format_name[0].lower() + format_name[1:]
    format_name = re.sub("__([A-Z])", lambda m: "+" + m.group(1).lower(), format_name)
    format_name = re.sub("_([A-Z])", lambda m: "." + m.group(1).lower(), format_name)
    format_name = re.sub("([A-Z])", lambda m: "-" + m.group(1).lower(), format_name)
    return format_name


def from_mime_format_name(format_name: str):
    if format_name.startswith("x-"):
        format_name = format_name[2:]
    if re.match(r"^[0-9]", format_name):
        format_name = "_" + format_name
    format_name = format_name.capitalize()
    format_name = re.sub(r"(\.)(\w)", lambda m: "_" + m.group(2).upper(), format_name)
    format_name = re.sub(r"(\+)(\w)", lambda m: "__" + m.group(2).upper(), format_name)
    format_name = re.sub(r"(-)(\w)", lambda m: m.group(2).upper(), format_name)
    return format_name


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


LIST_MIME = "+list-of"


def gen_filename(
    seed_or_rng: ty.Union[random.Random, int],
    file_type: ty.Type[fileformats.core.FileSet] = None,
    length: int = 32,
    stem: ty.Optional[str] = None,
):
    """Generates a random filename of length `length` and extension `ext`

    Parameters
    ----------
    seed_or_rng : random.Random or int
        used to seed the random number generator
    file_type : Type[FileSet], optional
        type of the file to generate the filename for, used to append any extensions
        and seed the random number generator if required
    length : int
        length of the filename (minus extension)
    stem : str, optional
        the stem to use for the filename if provided

    Returns
    -------
    filename : str
        randomly generated filename
    """
    if file_type is None:
        import fileformats.generic

        file_type = fileformats.generic.FsObject
    if stem:
        fname = stem
    else:
        if isinstance(seed_or_rng, random.Random):
            rng = seed_or_rng
        else:
            if not inspect.isclass(file_type):
                file_type = type(file_type)
            rng = random.Random(str(seed_or_rng) + file_type.mime_like)
        fname = "".join(rng.choices(string.ascii_letters + string.digits, k=length))
    if file_type and file_type.ext:
        fname += file_type.ext
    return fname
