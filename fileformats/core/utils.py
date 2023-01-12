import importlib
import re
import os
from contextlib import contextmanager
from fileformats.core.exceptions import FileFormatsError


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
    type_name, format_name = mime_string.split("/")
    if format_name.startswith("x-"):
        format_name = format_name[2:]
    format_name = format_name.capitalize()
    format_name = re.sub(r"(-)(\w)", lambda m: m.group(2).upper(), format_name)
    format_name = re.sub(r"(\+)(\w)", lambda m: "_" + m.group(2).upper(), format_name)
    module = importlib.import_module("fileformats." + type_name)
    return getattr(module, format_name)


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
    iana : bool
        whether to use standardised IANA format or a more relaxed type format corresponding
        to the fileformats extension the type belongs to

    Returns
    -------
    type
        the corresponding file format class
    """
    if iana and klass.iana is not None:
        return klass.iana
    format_name = klass.__name__
    format_name = format_name[0].lower() + format_name[1:]
    format_name = re.sub("_([A-Z])", lambda m: "+" + m.group(1).lower(), format_name)
    format_name = re.sub("([A-Z])", lambda m: "-" + m.group(1).lower(), format_name)
    if iana:
        mime = f"application/x-{format_name}"
    else:
        module_parts = klass.__module__.__name__.split(".")
        if module_parts[0] != "fileformats":
            raise FileFormatsError(
                f"Cannot create reversible MIME type for {klass} as it is not in the "
                "fileformats namespace"
            )
        type_name = module_parts[1]
        namespace_module = importlib.import_module("fileformats." + type_name)
        if getattr(namespace_module, klass.__name__, None) is not klass:
            raise FileFormatsError(
                f"Cannot create reversible MIME type for {klass} as it is not present in a "
                f"top-level fileformats namespace package ({klass.__module__.__name__}"
            )
        mime = f"{type_name}/{format_name}"
    return mime


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
