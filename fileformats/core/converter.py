import typing as ty
import attrs
from .utils import describe_task
from .exceptions import FileFormatsError


@attrs.define
class ConverterWrapper:
    """Wraps a converter task in a workflow so that the in_file and out_file names can
    be mapped onto their standardised names, "in_file" and "out_file" if necessary
    """

    task_spec: ty.Callable
    in_file: str = None
    out_file: str = None

    def __call__(self, name=None, **kwargs):
        from pydra.engine import Workflow

        if name is None:
            name = f"{self.task_spec.__name__}_wrapper"
        wf = Workflow(
            name=name, input_spec=list(set(["in_file"] + list(kwargs))), **kwargs
        )
        wf.add(self.task_spec(name="task", **{self.in_file: wf.lzin.in_file}))
        wf.set_output([("out_file", getattr(wf.task.lzout, self.out_file))])
        return wf


class SubtypeVar:
    """To handle the case where the target format is a placeholder (type-var) defined by
    by its relationship to the source format, e.g.

    AnyFileFormat = FileSet.type_var("AnyFileFormat")

    @converter
    @pydra.mark.task
    def unzip(in_file: Zip[AnyFileFormat], out_file: AnyFileFormat):
        ...
    """

    converters = {}

    def __init__(self, name: str, base: type):
        self.name = name
        self.base = base

    def __str__(self):
        return f"{self.base.__name__}:{self.name}"

    def __repr__(self):
        return f"SubtypeVar({str(self)})"

    def __hash__(self):
        return hash((type(self), self.base, self.name))

    @property
    def __name__(self):
        return self.name

    def is_subtype_of(self, super_type: type, allow_same: bool = True):
        """Check to see whether datatype class is a subtype of a given super class.
        In this case the subtype is expected to be able to be treated as if it was
        the super class.

        Overridden in the ``WithQualifiers`` mixin to add support for
        qualified subtypes

        Parameters
        ----------
        super_type : type
            the class to check whether the given class is a subtype of
        allow_same : bool, optional
            whether there is a match if the classes are the same, by default True

        Returns
        -------
        is_subtype : bool
            whether or not the current class can be considered a subtype of the super (or
            is the super itself)
        """
        return self.base.is_subtype_of(super_type, allow_same=allow_same)

    @classmethod
    def get_converter_tuples(
        cls, source_format: type, target_format: type
    ) -> ty.List[ty.Tuple[ty.Callable, ty.Dict[str, ty.Any]]]:
        # check to see whether there are converters from a base class of the source
        # format
        available_converters = []
        if source_format.is_qualified:
            for template_source_format, converter in cls.converters.items():
                if not template_source_format.unqualified.is_subtype_of(
                    source_format.unqualified
                ):
                    continue
                assert len(template_source_format.wildcard_qualifiers()) == 1
                non_wildcards = template_source_format.non_wildcard_qualifiers()
                if not non_wildcards.issubset(source_format.qualifiers):
                    continue
                from_types = tuple(
                    set(source_format.qualifiers).difference(non_wildcards)
                )
                if any(q.is_subtype_of(target_format) for q in from_types):
                    available_converters.append(converter)
        return available_converters

    @classmethod
    def register_converter(
        cls,
        source_format: type,
        converter_tuple: ty.Tuple[ty.Callable, ty.Dict[str, ty.Any]],
    ):
        """Registers a converter task within a class attribute. Called by the @fileformats.mark.converter
        decorator.

        Parameters
        ----------
        source_format : type
            the source format to register a converter from
        task_spec : ty.Callable
            a callable that resolves to a Pydra task
        converter_kwargs : dict
            additional keyword arguments to be passed to the task spec at initialisation
            time

        Raises
        ------
        FormatConversionError
            if there is already a converter registered between the two types
        """
        # Ensure "converters" dict is defined in the target class and not in a superclass
        if len(source_format.wildcard_qualifiers()) > 1:
            raise FileFormatsError(
                "Cannot register a conversion to a generic type from a type with more "
                f"than one wildcard {source_format} ({list(source_format.wildcard_qualifiers())})"
            )
        prev_registered = [
            f
            for f in cls.converters
            if (
                f.unqualified is source_format.unqualified
                and f.non_wildcard_qualifiers()
                == source_format.non_wildcard_qualifiers()
            )
        ]
        assert len(prev_registered) <= 1
        if prev_registered:
            prev = prev_registered[0]
            prev_task = cls.converters[prev][0]
            raise FileFormatsError(
                f"There is already a converter registered from {prev} "
                f"to the generic type '{tuple(prev.wildcard_qualifiers())[0]}':"
                f"{describe_task(prev_task)}"
            )

        cls.converters[source_format] = converter_tuple
