import importlib
from pathlib import Path
import inspect
import typing as ty
import re
import os
import pkgutil
from contextlib import contextmanager
from fileformats.core.exceptions import (
    MissingExtendedDepenciesError,
    FileFormatsError,
)
import fileformats.core


def find_matching(fspaths: ty.List[Path], standard_only: bool = False):
    """Detect the corresponding file format from a set of file-system paths

    Parameters
    ----------
    fspaths : list[Path]
        file-system paths to detect the format of
    standard_only : bool, optional
        If you only want to return matches from the "standard" IANA types
    """
    fspaths = fspaths_converter(fspaths)
    matches = []
    for frmt in fileformats.core.FileSet.all_formats:
        if frmt.matches(fspaths) and (
            not standard_only or frmt.namespace in STANDARD_NAMESPACES
        ):
            matches.append(frmt)
    return matches


def from_mime(mime_str: str):
    return fileformats.core.DataType.from_mime(mime_str)


def splitext(fspath: Path, multi=False):
    """splits an extension from the file stem, taking into consideration multi-part
    extensions such as ".nii.gz".

    Parameters
    ----------
    fspath : Path
        the file-system path to split the extension from
    multi : bool, optional
        whether to support multi-part extensions such as ".nii.gz". Note this means that
        it will match sections of file names with "."s in them, by default False

    Returns
    -------
    str
        file stem
    str
        file extension
    """
    if multi:
        ext = "".join(fspath.suffixes)
        stem = fspath.name[: -len(ext)]
    else:
        stem = fspath.stem
        ext = fspath.suffix
    return stem, ext


def subpackages():
    """Iterates over all subpackages within the fileformats namespace

    Yields
    ------
    module
        all modules within the package
    """
    for mod_info in pkgutil.iter_modules(
        fileformats.__path__, prefix=fileformats.__package__ + "."
    ):
        if mod_info.name == "core":
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
        ty.Iterable[ty.Union[str, os.PathLike, bytes]], str, os.PathLike, bytes
    ]
):
    """Ensures fs-paths are a set of pathlib.Path"""
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


class MissingExtendedDependency:
    """Used as a placeholder for package dependencies that are only installed with the
    "extended" install extra.

    Parameters
    ----------
    pkg_name : str
        name of the package to act as a placeholder for
    module_path : str
        path of the module, i.e. the value of the '__name__' global variable
    """

    def __init__(self, pkg_name: str, module_path: str):
        self.pkg_name = pkg_name
        module_parts = module_path.split(".")
        assert module_parts[0] == "fileformats"
        if module_parts[1] in STANDARD_NAMESPACES:
            self.required_in = "fileformats"
        else:
            self.required_in = f"fileformats-{module_parts[1]}"

    def __getattr__(self, _):
        raise MissingExtendedDepenciesError(
            f"Not able to access extended behaviour in {self.required_in} as required "
            f"package '{self.pkg_name}' was not installed. Please reinstall "
            f"{self.required_in} with 'extended' install extra to access extended "
            f"behaviour of the format classes (such as loading and conversion), i.e.\n\n"
            f"    $ python3 -m pip install {self.required_in}[extended]"
        )


STANDARD_NAMESPACES = [
    "archive",
    "audio",
    "document",
    "image",
    "numeric",
    "serialization",
    "text",
    "video",
]


def to_mime_format_name(format_name: str):
    if "___" in format_name:
        raise FileFormatsError(
            f"Cannot convert name of format class {format_name} to mime string as it "
            "contains triple underscore"
        )
    format_name = format_name[0].lower() + format_name[1:]
    format_name = re.sub("__([A-Z])", lambda m: "+" + m.group(1).lower(), format_name)
    format_name = re.sub("_([A-Z])", lambda m: "." + m.group(1).lower(), format_name)
    format_name = re.sub("([A-Z])", lambda m: "-" + m.group(1).lower(), format_name)
    return format_name


def from_mime_format_name(format_name: str):
    if format_name.startswith("x-"):
        format_name = format_name[2:]
    format_name = format_name.capitalize()
    format_name = re.sub(r"(\.)(\w)", lambda m: "_" + m.group(2).upper(), format_name)
    format_name = re.sub(r"(\+)(\w)", lambda m: "__" + m.group(2).upper(), format_name)
    format_name = re.sub(r"(-)(\w)", lambda m: m.group(2).upper(), format_name)
    return format_name


def hash_file(fspath: Path, chunk_len: int, crypto: ty.Callable):
    crypto_obj = crypto()
    with open(fspath, "rb") as fp:
        for chunk in iter(lambda: fp.read(chunk_len), b""):
            crypto_obj.update(chunk)
    return crypto_obj.hexdigest()


def hash_dir(
    fspath: Path,
    chunk_len: int,
    crypto: ty.Callable,
    ignore_hidden_files: bool = False,
    ignore_hidden_dirs: bool = False,
    relative_to: Path = None,
):
    if relative_to is None:
        relative_to = fspath
    file_hashes = {}
    for dpath, _, filenames in sorted(os.walk(fspath)):
        # Sort in-place to guarantee order.
        filenames.sort()
        dpath = Path(dpath)
        if ignore_hidden_dirs and dpath.name.startswith(".") and str(dpath) != fspath:
            continue
        for filename in filenames:
            if ignore_hidden_files and filename.startswith("."):
                continue
            file_hashes[str((dpath / filename).relative_to(relative_to))] = hash_file(
                dpath / filename, crypto=crypto, chunk_len=chunk_len
            )
    return file_hashes


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
