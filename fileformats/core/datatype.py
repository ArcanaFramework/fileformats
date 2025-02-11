from __future__ import annotations
from inspect import isclass
import typing as ty
from fileformats.core.typing import Self
from abc import ABCMeta
import importlib
import itertools
from .exceptions import (
    FileFormatsError,
    FormatMismatchError,
    FormatConversionError,
    FormatRecognitionError,
)
from .decorators import classproperty
from .utils import (
    subpackages,
    add_exc_note,
)
from .identification import (
    to_mime_format_name,
    from_mime_format_name,
    IANA_MIME_TYPE_REGISTRIES,
)
from .classifier import Classifier

if ty.TYPE_CHECKING:
    from .converter_helpers import Converter


class DataType(Classifier, metaclass=ABCMeta):
    """
    Base class for all file formats and fields.
    """

    is_fileset = False
    is_field = False

    @classproperty
    def nested_types(cls) -> ty.Tuple[ty.Type[Classifier], ...]:
        return ()

    # Store converters registered by @converter decorator that convert to FileSet
    # NB: each class will have its own version of this dictionary
    converters: ty.Dict[
        ty.Type["DataType"], "fileformats.core.converter_helpers.Converter"  # type: ignore[type-arg]
    ] = {}

    @classmethod
    def type_var(cls, name: str) -> "fileformats.core.converter_helpers.SubtypeVar":
        import fileformats.core.converter_helpers

        return fileformats.core.converter_helpers.SubtypeVar.new(name, cls)

    @classmethod
    def matches(cls, values: ty.Any) -> bool:
        """Checks whether the given value (fspaths for file-sets) match the datatype
        specified by the class

        Parameters
        ----------
        values : ty.Any
            values to check whether they match the given datatype

        Returns
        -------
        matches : bool
            whether the datatype matches the provided values
        """
        try:
            cls(values)  # type: ignore
        except FormatMismatchError:
            return False
        else:
            return True

    @classproperty  # type: ignore[arg-type]
    def all_types(self) -> ty.Iterator[ty.Type[DataType]]:
        return itertools.chain(FileSet.all_formats, Field.all_fields)

    @classmethod
    def subclasses(cls) -> ty.Generator[ty.Type[Self], None, None]:
        """Iterate over all installed subclasses"""
        for subpkg in subpackages():
            for attr_name in dir(subpkg):
                attr = getattr(subpkg, attr_name)
                if (
                    attr is not cls
                    and isclass(attr)
                    and issubclass(attr, cls)
                    and ty.get_origin(attr) is None
                ):
                    yield attr

    @classmethod
    def get_converter(
        cls,
        source_format: ty.Type[DataType],
    ) -> "Converter | None":
        if issubclass(source_format, cls):
            return None
        else:
            raise FormatConversionError(
                f"Cannot converter between '{cls.mime_like}' and '{source_format.mime_like}'"
            )

    @classproperty  # type: ignore[arg-type]
    def mime_type(cls) -> str:
        """Generates a MIME type identifier from a format class (i.e. an identifier
        for a non-MIME class in the MIME."""
        raise FileFormatsError(f"MIME type not defined for {cls} class")

    @classproperty  # type: ignore[arg-type]
    def mime_like(cls) -> str:
        """Generates a "MIME-like" identifier from a format class. The fileformats
        package namespace forms a superset of IANA MIME registries. Formats with
        official MIME types will return their MIME type, while extension formats will
        return a MIME-like identifier, e.g. "text/plain" for fileformats.text.Plain.
        and "medimage/nifti" for fileformats.medimage.Nifti.
        """
        return f"{cls.namespace}/{to_mime_format_name(cls.__name__)}"  # type: ignore

    @classmethod
    def from_mime(cls, mime_string: str) -> ty.Type[DataType]:
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

        Raises
        ------
        FormatRecognitionError
            if the MIME string does not correspond to a valid file format class
        """
        try:
            namespace, format_name = mime_string.split("/")
        except ValueError:
            raise FormatRecognitionError(
                f"Format '{mime_string}' is not a valid MIME-like format of <namespace>/<format>"
            ) from None
        else:
            namespace = namespace.replace("-", "_")
        # Attempt to load file type using their `iana_mime` attribute
        try:
            return FileSet.formats_by_iana_mime[mime_string]  # type: ignore[no-any-return]
        except KeyError:
            pass
        if namespace == "application" and format_name.startswith("x-"):
            # We treat the "application/x-" namespace as a catch-all for any formats
            # that are not explicitly covered by the IANA standard (which is how the IANA
            # treats it). Therefore, we loop through all subclasses across the different
            # namespaces to find one that matches the name.
            format_name = format_name[2:]  # remove "x-" prefix
            matching_name: ty.Collection[
                ty.Type[FileSet]
            ] = FileSet.formats_by_name.get(format_name, ())
            matching_name = [
                m
                for m in matching_name
                if m.__module__ not in IANA_MIME_TYPE_REGISTRIES
            ]
            if not matching_name:
                namespace_names = [
                    p.__name__
                    for p in subpackages()
                    if p.__name__.split(".")[-1] not in IANA_MIME_TYPE_REGISTRIES
                ]
                class_name = from_mime_format_name(format_name)
                raise FormatRecognitionError(
                    f"Did not find class matching extension the class name '{class_name}' "
                    f"corresponding to MIME type '{mime_string}' "
                    f"in any of the installed nonnamespaces: {namespace_names}"
                )
            elif len(matching_name) > 1:
                namespace_names = [f.__module__ for f in matching_name]
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
                if "+" in format_name:
                    parent_namespace: ty.Optional[str]
                    if "_" in namespace:
                        parent_namespace = namespace.split("_")[0]
                        parent_module = importlib.import_module(
                            "fileformats." + parent_namespace
                        )
                    else:
                        parent_namespace = parent_module = None

                    def get_format(mime_name: str) -> ty.Type[DataType]:
                        name = from_mime_format_name(mime_name)
                        try:
                            return getattr(module, name)  # type: ignore
                        except AttributeError:
                            if parent_module:
                                try:
                                    return getattr(parent_module, name)  # type: ignore
                                except AttributeError:
                                    pass
                                err_msg_part = f" or fileformats.{parent_namespace}"
                            else:
                                err_msg_part = ""
                            raise FormatRecognitionError(
                                f"Could not load format class {name} (from "
                                f"'{mime_name}') fileformats.{namespace}"
                                f"{err_msg_part} corresponding "
                                f"to MIME, or MIME-like, type {mime_string}"
                            ) from None

                    classifiers_str, classified_name = format_name.split("+")
                    classifiers = [get_format(c) for c in classifiers_str.split(".")]
                    try:
                        classified = get_format(classified_name)
                    except FormatRecognitionError as e:
                        try:
                            classified = cls.generically_classifiable_by_name[
                                classified_name
                            ]
                        except KeyError:
                            add_exc_note(
                                e,
                                (
                                    "neither list of generic types "
                                    f"({list(cls.generically_classifiable_by_name)})"
                                ),
                            )
                            raise e
                    klass = classified[classifiers]  # type: ignore
                else:
                    raise FormatRecognitionError(
                        f"Did not find '{class_name}' class in fileformats.{namespace} "
                        f"corresponding to MIME, or MIME-like, type {mime_string}"
                    ) from None
        if not issubclass(klass, cls):
            raise FormatRecognitionError(
                f"Class '{klass}' does not inherit from '{cls}'"
            )
        return klass

    @classproperty  # type: ignore[arg-type]
    def generically_classifiable_by_name(cls) -> ty.Dict[str, ty.Type[DataType]]:
        if cls._generically_classifiable_by_name is None:
            cls._generically_classifiable_by_name = {
                to_mime_format_name(f.__name__): f
                for f in FileSet.all_formats
                if getattr(f, "generically_classifiable", False)
            }
        return cls._generically_classifiable_by_name

    # Register all generically classified types
    _generically_classifiable_by_name: ty.Optional[
        ty.Dict[str, ty.Type[DataType]]
    ] = None

    REQUIRED_ANNOTATION = "__fileformats_required__"
    CHECK_ANNOTATION = "__fileformats_check__"


from .fileset import FileSet  # noqa
from .field import Field  # noqa
import fileformats.core.converter_helpers  # noqa
