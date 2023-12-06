import importlib
import typing as ty
import inspect
from itertools import zip_longest
import functools
import attrs
import urllib.error
from .datatype import DataType
from .converter import ConverterWrapper
from .exceptions import FormatConversionError, FileFormatsExtrasError
from .utils import import_extras_module, check_package_exists_on_pypi


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

    prop.fget.__annotations__[DataType.REQUIRED_ANNOTATION] = None
    return prop


def check(method):
    """Decorator that flags a method as being a special boolean method that needs to
    return True for the format to be considered a match

    Parameters
    ----------
    method : Function
        the method to hook as a check
    """
    method.__annotations__[DataType.CHECK_ANNOTATION] = None
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
        out_file_local = out_file
        if source_format is None or target_format is None:
            task = task_spec()
        if source_format is None:
            inputs_dict = attrs.fields_dict(type(task.inputs))
            source = inputs_dict[in_file].type
        else:
            source = source_format
        if target_format is None:
            outputs_dict = attrs.fields_dict(make_klass(task.output_spec))
            try:
                target = outputs_dict[out_file].type
            except KeyError:
                # If there isn't an 'out_file' field but there is only one output field
                # with the default name of 'out' use that instead
                if out_file == "out_file" and list(outputs_dict.keys()) == ["out"]:
                    out_file_local = "out"
                    target = outputs_dict["out"].type
                else:
                    raise
        else:
            target = target_format
        # Handle string annotations
        if isinstance(source, str) or isinstance(target, str):
            module_dict = importlib.import_module(task_spec.__module__).__dict__
            if isinstance(source, str):
                source = eval(source, module_dict)
            if isinstance(target, str):
                target = eval(target, module_dict)
        if not issubclass(target, DataType):
            raise FormatConversionError(
                f"Target file format '{target.__name__}' is not of subtype of "
                "fileformats.core.DataType"
            )
        if in_file != "in_file" or out_file_local != "out_file":
            task_spec = ConverterWrapper(
                task_spec,
                in_file=in_file,
                out_file=out_file_local,
            )
        target.register_converter(
            source_format=source, converter_tuple=(task_spec, converter_kwargs)
        )
        return task_spec

    return decorator if task_spec is None else decorator(task_spec)


def extra(method: ty.Callable):
    """A decorator which uses singledispatch to facilitate the registering of
    "extra" functionality in external packages (e.g. "fileformats-extras")"""

    dispatch_method = functools.singledispatch(method)

    @functools.wraps(method)
    def decorated(obj, *args, **kwargs):
        cls = type(obj)
        extras = []
        for tp in cls.referenced_types():
            extras.append(import_extras_module(tp))
        try:
            return dispatch_method(obj, *args, **kwargs)
        except NotImplementedError:
            msg = f"No implementation for '{method.__name__}' extra for {cls.__name__} types"
            for extra in extras:
                if not extra.imported:
                    try:
                        if check_package_exists_on_pypi(extra.pypi):
                            msg += (
                                f'. An "extras" package exists on PyPI ({extra.pypi}), '
                                "which may contain an implementation, try installing it "
                                f"(e.g. 'pip install {extra.pypi}') and check again"
                            )
                    except urllib.error.URLError:
                        msg += (
                            '. Was not able to check whether an "extras" package '
                            f"({extra.pypi}) exists on PyPI or not"
                        )
            raise FileFormatsExtrasError(msg)

    decorated.register = ExtraRegisterer(dispatch_method)
    return decorated


class ExtraRegisterer:
    def __init__(self, dispatch):
        self.dispatch = dispatch

    def __call__(self, function: ty.Callable):
        method = self.dispatch.__wrapped__
        msig = inspect.signature(method)
        fsig = inspect.signature(function)

        def type_match(a, b) -> bool:
            return isinstance(a, str) or isinstance(b, str) or a == b

        differences = []
        for i, (mparam, fparam) in enumerate(
            zip_longest(
                list(msig.parameters.values())[1:], list(fsig.parameters.values())[1:]
            )
        ):
            if mparam is None:
                differences.append(
                    f"found additional argument, '{fparam.name}', at position {i}"
                )
                continue
            if fparam is None:
                if mparam.default is mparam.empty:
                    differences.append(
                        f"override missing required argument '{mparam.name}'"
                    )
                continue
            mname = mparam.name
            fname = fparam.name
            mtype = mparam.annotation
            ftype = fparam.annotation
            if mname != fname:
                differences.append(
                    f"name of parameter at position {i}: {mname} vs {fname}"
                )
            elif not type_match(mtype, ftype):
                differences.append(f"Type of '{mname}' arg: {mtype} vs {ftype}")
        if not type_match(msig.return_annotation, fsig.return_annotation):
            differences.append(
                f"return type: {msig.return_annotation} vs {fsig.return_annotation}"
            )
        if differences:
            raise TypeError(
                f"Arguments differ between the signature of the "
                f"decorated method {method} and the registered override {function}:\n"
                + "\n".join(differences)
            )
        return self.dispatch.register(function)
