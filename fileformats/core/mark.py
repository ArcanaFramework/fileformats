from __future__ import annotations
import inspect
import operator
from .base import FileSet, REQUIRED_ANNOTATION, CHECK_ANNOTATION
from .exceptions import FileFormatError


__all__ = ["required", "check", "converter"]


def required(property=None, **checks):
    """Decorator that flags a property of a file-set as being required for the format
    specified by the class.

    Parameters
    ----------
    property : property, optional
        the property to decorate, if provided the decorator is assumed to wrap the
        property directly, otherwise a wrapping decorator is returned instead
    **checks: dict[str, Any]
        checks to run against the value of the property to determine whether the
        file-set is in the format specified by the class. Keys should correspond to
        binary operators in the "operators" module, and values are the second operand
        to pass to the operator (the value of the property will be the first operand)
    """
    return _property_check_decorator(property, checks, REQUIRED_ANNOTATION)


def check(property=None, **checks):
    """Decorator that flags a property of a file-set as being required for the format
    specified by the class if the "checks" flag of the file-set has been set to true

    Parameters
    ----------
    property : property, optional
        the property to decorate, if provided the decorator is assumed to wrap the
        property directly, otherwise a wrapping decorator is returned instead
    **checks: dict[str, Any]
        checks to run against the value of the property to determine whether the
        file-set is in the format specified by the class. Keys should correspond to
        binary operators in the "operators" module, and values are the second operand
        to pass to the operator (the value of the property will be the first operand)
    """
    return _property_check_decorator(property, checks, CHECK_ANNOTATION)


def converter(
    task_spec=None,
    source_format=None,
    target_format=None,
    in_file="in_file",
    out_file=None,
):
    """Decorator that registers a task as a converter between a source and target format
    pair

    Parameters
    ----------
    task : pydra.engine.core.TaskBase, optional
        the Pydra task to register as a converter, if provided the decorator is assumed
        to wrap the task spec directly, otherwise a wrapping decorator is returned instead
    source_format: type, optional
        file-format type to convert from, detected from type of "in_file" by default
    target_format: type, optional
        file-format type to convert to, detected from type of "out_file" by default None
    in_file : str, optional
        name of the input to be considered the "in_file", by default "in_file"
    out_file : _type_, optional
        name of the output to be considered the "out_file",
        by default "out_file" and "out" and will be tried in that order
    """
    # Note if explicit value for out_file isn't provided note it so we can also try
    # "out"
    if out_file is None:
        default_out = True
        out_file = "out_file"

    def decorator(task_spec):
        task = task_spec()
        source = getattr(task, in_file).type if source_format is None else source_format
        if target_format is None:
            try:
                target = getattr(task, out_file).type
            except AttributeError:
                if default_out:
                    target = getattr(task, "out").type
                else:
                    raise
        else:
            target = target_format
        if not issubclass(target, FileSet):
            raise FileFormatError(
                f"Target file format {target.__name__} is not of sub-class of "
                "FileSet"
            )
        # Get "converters" dictionary of class
        try:
            converters = target.__dict__["converters"]
        except KeyError:
            converters = target.__dict__["converters"] = {}
        if source in converters:
            msg = (
                f"There is already a converter registered between {source.__name__} "
                f"and {target.__name__}: {converters[source]}"
            )
            src_file = inspect.getsourcefile(converters[source])
            src_line = inspect.getsourcelines(converters[source])[-1]
            msg += f" (defined at line {src_line} of {src_file})"
            raise FileFormatError(msg)
        if in_file != "in_file" or out_file != "out_file":
            from .converter import ConverterWrapper

            task_spec = ConverterWrapper(task_spec, in_file=in_file, out_file=out_file)
        converters[source] = task_spec
        return task_spec

    return decorator if task_spec is None else decorator(task_spec)


def _property_check_decorator(property, checks, annotation):
    for op in checks:
        if not hasattr(operator, op):
            raise RuntimeError(
                f'Check {op} does not correspond to an operator in the "operator" module'
            )
    property.__annotations__[annotation] = checks
