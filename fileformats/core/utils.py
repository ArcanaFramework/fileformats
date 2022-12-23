from pydra.engine.task import FunctionTask
from pydra.engine.specs import BaseSpec, SpecInfo


# Tools imported from Arcana, will remove again once file-formats and "cells"
# have been split
CONVERTER_ANNOTATIONS = "__fileformats_converter__"
HASH_CHUNK_SIZE = 2**20  # 1MB in calc. checksums to avoid mem. issues


# Escape values for invalid characters for Python variable names
PATH_ESCAPES = {
    "_": "_u_",
    "/": "__l__",
    ".": "__o__",
    " ": "__s__",
    "\t": "__t__",
    ",": "__comma__",
    ">": "__gt__",
    "<": "__lt__",
    "-": "__H__",
    "'": "__singlequote__",
    '"': "__doublequote__",
    "(": "__openparens__",
    ")": "__closeparens__",
    "[": "__openbracket__",
    "]": "__closebracket__",
    "{": "__openbrace__",
    "}": "__closebrace__",
    ":": "__colon__",
    ";": "__semicolon__",
    "`": "__tick__",
    "~": "__tilde__",
    "|": "__pipe__",
    "?": "__question__",
    "\\": "__backslash__",
    "$": "__dollar__",
    "@": "__at__",
    "!": "__exclaimation__",
    "#": "__pound__",
    "%": "__percent__",
    "^": "__caret__",
    "&": "__ampersand__",
    "*": "__star__",
    "+": "__plus__",
    "=": "__equals__",
    "XXX": "__tripplex__",
}

PATH_NAME_PREFIX = "XXX"

EMPTY_PATH_NAME = "__empty__"


def path2varname(path):
    """Escape a string (typically a file-system path) so that it can be used as a Python
    variable name by replacing non-valid characters with escape sequences in PATH_ESCAPES.

    Parameters
    ----------
    path : str
        A path containing '/' characters that need to be escaped

    Returns
    -------
    str
        A python safe name
    """
    if not path:
        name = EMPTY_PATH_NAME
    else:
        name = path
        for char, esc in PATH_ESCAPES.items():
            name = name.replace(char, esc)
    if name.startswith("_"):
        name = PATH_NAME_PREFIX + name
    return name


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


def func_task(func, in_fields, out_fields, **inputs):
    """Syntactic sugar for creating a FunctionTask

    Parameters
    ----------
    func : Callable
        The function to wrap
    input_fields : ty.List[ty.Tuple[str, type]]
        The list of input fields to create for the task
    output_fields : ty.List[ty.Tuple[str, type]]
        The list of output fields to create for the task
    **inputs
        Inputs to set for the task

    Returns
    -------
    pydra.FunctionTask
        The wrapped task"""
    func_name = func.__name__.capitalize()
    return FunctionTask(
        func,
        input_spec=SpecInfo(name=f"{func_name}In", bases=(BaseSpec,), fields=in_fields),
        output_spec=SpecInfo(
            name=f"{func_name}Out", bases=(BaseSpec,), fields=out_fields
        ),
        **inputs,
    )
