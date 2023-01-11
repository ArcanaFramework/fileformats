import importlib
import re


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
    klass_name = re.sub(
        r"(-)(\w)", lambda m: m.group(2).upper(), format_name.capitalize()
    )
    module = importlib.import_module("fileformats." + type_name)
    return getattr(module, klass_name)


def to_mime(klass):
    """Generates a MIME (IANA) or "MIME-like" identifier from a format class (i.e.
    an identifier for a non-MIME class in the MIME style), e.g.

        fileformats.text.Plain to "text/plain"

    and

        fileformats.image.TiffFx to "image/tiff-fx"

    Parameters
    ----------
    klass : type(FileSet)
        FileSet subclass

    Returns
    -------
    type
        the corresponding file format class
    """
    klass_name = klass.__name__
    format_name = klass_name[0].lower() + re.sub(
        "([A-Z])", lambda m: "-" + m.group(1).lower(), klass_name[1:]
    )
    type_name = klass_name.__module__.__name__.split(".")[-1]
    return f"{type_name}/{format_name}"


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
