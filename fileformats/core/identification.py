import operator
from pathlib import Path
import typing as ty
import re
from fileformats.core.exceptions import (
    FileFormatsError,
    FormatRecognitionError,
)
import fileformats.core
from .utils import fspaths_converter, add_exc_note


LIST_MIME = "+list-of"
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
    # Handle case
    if isinstance(datatype, ty.ForwardRef):
        datatype = datatype.__forward_arg__
    if (
        isinstance(datatype, str)
        and datatype.startswith("fileformats.")
        and not official
    ):
        ns, class_name = datatype.split(".")[1:]
        ns = ns.replace("_", "-")
        class_name = to_mime_format_name(class_name)
        return ns + "/" + class_name
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
    *candidates: ty.Tuple[ty.Type["fileformats.core.FileSet"]],
    common_ok: bool = False,
    ignore: ty.Optional[str] = None,
    **kwargs,
) -> ty.List["fileformats.core.FileSet"]:
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
