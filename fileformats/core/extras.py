import importlib
import typing as ty
import inspect
from itertools import zip_longest
import functools
import urllib.error
import fileformats.core
from typing_extensions import TypeAlias
from .datatype import DataType
from .converter_helpers import ConverterWrapper, ConverterSpec, SubtypeVar
from .exceptions import FormatConversionError, FileFormatsExtrasError
from .utils import import_extras_module, check_package_exists_on_pypi, add_exc_note

if ty.TYPE_CHECKING:
    from pydra.engine.core import TaskBase

WrappedTask = ty.TypeVar("WrappedTask", bound=ty.Callable[..., ty.Any])

FormatType: TypeAlias = ty.Union[ty.Type["fileformats.core.FileSet"], SubtypeVar, None]


def converter(
    task_spec: "TaskBase" = None,
    source_format: FormatType = None,
    target_format: FormatType = None,
    in_file: str = "in_file",
    out_file: str = "out_file",
    **converter_kwargs: ty.Any,
) -> ty.Callable[[WrappedTask], WrappedTask]:
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

    try:
        import attrs
    except ImportError as e:
        add_exc_note(
            e,
            "To use the 'converter' decorator you need to have the 'attrs' package "
            "installed, this should be installed with Pydra by default",
        )
        raise e

    def decorator(
        task_spec: ty.Type["TaskBase"],
    ) -> ty.Union[ty.Type["TaskBase"], ConverterWrapper]:
        out_file_local = out_file
        if source_format is None or target_format is None:
            task = task_spec()
        source: FormatType
        target: FormatType
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
        assert inspect.isclass(source) and inspect.isclass(target)
        if not issubclass(target, fileformats.core.FileSet):
            raise FormatConversionError(
                f"Target file format '{target.__name__}' is not of subtype of "
                "fileformats.core.FileSet"
            )
        wrapped_task_spec: ty.Union[ty.Type["TaskBase"], ConverterWrapper]
        if in_file != "in_file" or out_file_local != "out_file":
            wrapped_task_spec = ConverterWrapper(
                task_spec,
                in_file=in_file,
                out_file=out_file_local,
            )
        else:
            wrapped_task_spec = task_spec
        target.register_converter(
            source_format=source,
            converter_spec=ConverterSpec(wrapped_task_spec, converter_kwargs),
        )
        return wrapped_task_spec

    # We pretend to return the original function, instead of the Pydra task or ConverterWrapper
    return decorator if task_spec is None else decorator(task_spec)  # type: ignore[return-value]


ExtraImplementation = ty.TypeVar("ExtraImplementation", bound=ty.Callable[..., ty.Any])


class ExtraRegisterer:
    def __init__(self, dispatch: ty.Callable[..., ty.Any]) -> None:
        self.dispatch = dispatch

    def __call__(self, function: ExtraImplementation) -> ExtraImplementation:
        method = self.dispatch.__wrapped__  # type: ignore[attr-defined]
        msig = inspect.signature(method)
        fsig = inspect.signature(function)

        def type_match(a: ty.Union[str, type], b: ty.Union[str, type]) -> bool:
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
        return self.dispatch.register(function)  # type: ignore[attr-defined, no-any-return]


ExtraHookMethod: TypeAlias = ty.Callable[..., ty.Any]


class extra:
    """A decorator which uses singledispatch to facilitate the registering of
    "extra" functionality in external packages (e.g. "fileformats-extras")"""

    method: ExtraHookMethod
    dispatch_method: ty.Callable[..., ty.Any]
    register: "ExtraRegisterer"

    def __init__(self, method: ExtraHookMethod):
        self.method = method
        self.dispatch_method = functools.singledispatch(method)
        self.register = ExtraRegisterer(self.dispatch_method)

    def __call__(self, obj: DataType, *args: ty.Any, **kwargs: ty.Any) -> ty.Any:
        cls = type(obj)
        extras = []
        for tp in cls.referenced_types():  # type: ignore[attr-defined]
            extras.append(import_extras_module(tp))
        try:
            return self.dispatch_method(obj, *args, **kwargs)
        except NotImplementedError:
            msg = (
                f"No implementation for '{self.method.__name__}' extra for "
                f"{cls.__name__} types"
            )
            for xtra in extras:
                if not xtra.imported:
                    try:
                        if xtra.pypi and check_package_exists_on_pypi(xtra.pypi):
                            msg += (
                                f'. An "extras" package exists on PyPI ({xtra.pypi}), '
                                "which may contain an implementation, try installing it "
                                f"(e.g. 'pip install {xtra.pypi}') and check again"
                            )
                    except urllib.error.URLError:
                        msg += (
                            '. Was not able to check whether an "extras" package '
                            f"({xtra.pypi}) exists on PyPI or not"
                        )
            raise FileFormatsExtrasError(msg)
