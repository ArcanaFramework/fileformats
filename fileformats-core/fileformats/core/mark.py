from __future__ import annotations
import inspect
import attrs
from .base import FileSet, REQUIRED_ANNOTATION, CHECK_ANNOTATION
from .exceptions import FormatConversionError


__all__ = ["required", "check", "converter"]


def required(prop):
    """Decorator that flags a property of a file-set as being required for the format
    specified by the class.

    Parameters
    ----------
    prop : property, optional
        the property to decorate, if provided the decorator is assumed to wrap the
        property directly, otherwise a wrapping decorator is returned instead
    **checks: dict[str, Any]
        checks to run against the value of the property to determine whether the
        file-set is in the format specified by the class. Keys should correspond to
        binary operators in the "operators" module, and values are the second operand
        to pass to the operator (the value of the property will be the first operand)
    """

    prop.fget.__annotations__[REQUIRED_ANNOTATION] = None
    return prop


def check(method):
    """Decorator that flags a method as being a special boolean method that needs to
    return True for the format to be considered a match

    Parameters
    ----------
    method : Function
        the method to mark as a check
    """
    method.__annotations__[CHECK_ANNOTATION] = None
    return method


def converter(
    task_spec=None,
    source_format=None,
    target_format=None,
    in_file="in_file",
    out_file="out_file",
    **converter_kwargs,
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
    **converter_kwargs
        keyword arguments passed on to the converter task
    """
    # Note if explicit value for out_file isn't provided note it so we can also try
    # "out"
    from pydra.engine.helpers import make_klass

    def decorator(task_spec):
        if source_format is None or target_format is None:
            task = task_spec()
        if source_format is None:
            inputs_dict = attrs.fields_dict(type(task.inputs))
            source = inputs_dict[in_file].type
        else:
            source = source_format
        if target_format is None:
            outputs_dict = attrs.fields_dict(make_klass(task.output_spec))
            target = outputs_dict[out_file].type
        else:
            target = target_format
        if not issubclass(target, FileSet):
            raise FormatConversionError(
                f"Target file format {target.__name__} is not of sub-class of "
                "FileSet"
            )
        # Ensure "converters" dict is defined in the target class and not in a superclass
        if "converters" not in target.__dict__:
            target.converters = {}
        if source in target.converters:
            msg = (
                f"There is already a converter registered between {source.__name__} "
                f"and {target.__name__}: {target.converters[source]}"
            )
            src_file = inspect.getsourcefile(target.converters[source])
            src_line = inspect.getsourcelines(target.converters[source])[-1]
            msg += f" (defined at line {src_line} of {src_file})"
            raise FormatConversionError(msg)
        if in_file != "in_file" or out_file != "out_file":
            from .converter import ConverterWrapper

            task_spec = ConverterWrapper(task_spec, in_file=in_file, out_file=out_file)
        target.converters[source] = (task_spec, converter_kwargs)
        return task_spec

    return decorator if task_spec is None else decorator(task_spec)
