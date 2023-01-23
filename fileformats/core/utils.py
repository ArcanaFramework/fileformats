from __future__ import annotations
import importlib
import re
from warnings import warn
from pathlib import Path
import os
import traceback
import pkgutil
from contextlib import contextmanager
from fileformats.core.exceptions import (
    FileFormatsError,
    FormatRecognitionError,
    MissingExtendedDepenciesError,
)
import fileformats.core


def to_mime(klass, iana=True):
    """Generates a MIME (IANA) or "MIME-like" identifier from a format class (i.e.
    an identifier for a non-MIME class in the MIME style), e.g.

        fileformats.text.Plain to "text/plain"

    and

        fileformats.image.TiffFx to "image/tiff-fx"

    Parameters
    ----------
    klass : type(FileSet)
        FileSet subclass
    iana_mime : bool
        whether to use standardised IANA format or a more relaxed type format corresponding
        to the fileformats extension the type belongs to

    Returns
    -------
    type
        the corresponding file format class
    """
    if iana and getattr(klass, "iana_mime", None) is not None:
        return klass.iana_mime
    format_name = to_mime_format_name(klass.__name__)
    if iana:
        mime = f"application/x-{format_name}"
    else:
        namespace_module = importlib.import_module("fileformats." + klass.namespace)
        if getattr(namespace_module, klass.__name__, None) is not klass:
            raise FileFormatsError(
                f"Cannot create reversible MIME type for {klass} as it is not present in a "
                f"top-level fileformats namespace package '{klass.namespace}'"
            )
        mime = f"{klass.namespace}/{format_name}"
    return mime


def from_mime(mime_string):
    """Resolves a FileFormat class from a MIME (IANA) or "MIME-like" identifier (i.e.
    an identifier for a non-MIME class in the MIME style), e.g.

        "text/plain" resolves to fileformats.text.Plain

    and

        "image/tiff-fx" resolves to fileformats.image.TiffFx

    Parameters
    ----------
    mime_string : str
        MIME identifier

    Returns
    -------
    type
        the corresponding file format class
    """
    namespace, format_name = mime_string.split("/")
    try:
        return fileformats.core.FileSet.formats_by_iana_mime[mime_string]
    except KeyError:
        pass
    if namespace == "application":
        # We treat the "application" namespace as a catch-all for any formats that are
        # not explicitly covered by the IANA standard (which is kind of how the IANA
        # treats it). Therefore, we loop through all subclasses across the different
        # namespaces to find one that matches the name.
        if not format_name.startswith("x-"):
            raise FormatRecognitionError(
                "Did not find class matching official (i.e. non-extension) MIME type "
                f"{mime_string} (i.e. one not starting with 'application/x-'"
            ) from None
        format_name = format_name[2:]  # remove "x-" prefix
        matching_name = fileformats.core.FileSet.formats_by_name[format_name]
        if not matching_name:
            namespace_names = [n.__name__ for n in subpackages()]
            class_name = from_mime_format_name(format_name)
            raise FormatRecognitionError(
                f"Did not find class matching extension the class name '{class_name}' "
                f"corresponding to MIME type '{mime_string}' "
                f"in any of the installed namespaces: {namespace_names}"
            )
        elif len(matching_name) > 1:
            namespace_names = [f.__module__.__name__ for f in matching_name]
            raise FormatRecognitionError(
                f"Ambiguous extended MIME type '{mime_string}', could refer to "
                f"{', '.join(repr(f) for f in matching_name)} installed types. "
                f"Explicitly set the 'iana_mime' attribute on one or all of these types "
                f"to disambiguate, or uninstall all but one of the following "
                "namespaces: "
            )
        else:
            klass = next(iter(matching_name))
    else:
        class_name = from_mime_format_name(format_name)
        try:
            module = importlib.import_module("fileformats." + namespace)
        except ImportError:
            raise FormatRecognitionError(
                f"Did not find fileformats namespace package corresponding to {namespace} "
                f"required to interpret '{mime_string}' MIME, or MIME-like, type. "
                f"try installing the namespace package with "
                f"'python3 -m pip install fileformats-{namespace}'."
            ) from None
        try:
            klass = getattr(module, class_name)
        except AttributeError:
            raise FormatRecognitionError(
                f"Did not find '{class_name}' class in fileformats.{namespace} "
                f"corresponding to MIME, or MIME-like, type {mime_string}"
            ) from None
    return klass


def find_matching(fspaths: list[Path], standard_only: bool = False):
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
        if frmt.matches(fspaths) and frmt.namespace in STANDARD_NAMESPACES:
            matches.append(frmt)
    return matches


def to_mime_format_name(format_name):
    format_name = format_name[0].lower() + format_name[1:]
    format_name = re.sub("_([A-Z])", lambda m: "+" + m.group(1).lower(), format_name)
    format_name = re.sub("([A-Z])", lambda m: "-" + m.group(1).lower(), format_name)
    return format_name


def from_mime_format_name(format_name):
    if format_name.startswith("x-"):
        format_name = format_name[2:]
    format_name = format_name.capitalize()
    format_name = re.sub(r"(-)(\w)", lambda m: m.group(2).upper(), format_name)
    format_name = re.sub(r"(\+)(\w)", lambda m: "_" + m.group(2).upper(), format_name)
    return format_name


def splitext(fspath, multi=False):
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
def set_cwd(path):
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


def fspaths_converter(fspaths):
    """Ensures fs-paths are a set of pathlib.Path"""
    if isinstance(fspaths, (str, Path, bytes)):
        fspaths = [fspaths]
    return set((Path(p) if isinstance(p, str) else p).absolute() for p in fspaths)


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


def import_converters(module_name):
    """Attempts to import converters and raises warning if they can be imported"""
    try:
        importlib.import_module(module_name + ".converters")
    except ImportError:
        namespace = module_name.split(".")[1]
        if namespace in STANDARD_NAMESPACES:
            subpkg = ""
        else:
            subpkg = f"-{namespace}"
        warn(
            f"could not import converters for {module_name} module, please install with "
            f"the 'extended' install option to use converters for {module_name}, i.e.\n\n"
            f"$ python3 -m pip install fileformats{subpkg}[extended]:\n\n"
            f"Import error was:\n{traceback.format_exc()}"
        )


STANDARD_NAMESPACES = [
    "archive",
    "audio",
    "document",
    "generic",
    "image",
    "numeric",
    "serialization",
    "text",
    "video",
]
