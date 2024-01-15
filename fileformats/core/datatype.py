from __future__ import annotations
from inspect import isclass
from abc import ABCMeta
import importlib
import itertools
from .converter import SubtypeVar
from .exceptions import (
    FileFormatsError,
    FormatMismatchError,
    FormatConversionError,
    FormatRecognitionError,
)
from .utils import (
    classproperty,
    subpackages,
    to_mime_format_name,
    from_mime_format_name,
    IANA_MIME_TYPE_REGISTRIES,
)
from .classifier import Classifier


class DataType(Classifier, metaclass=ABCMeta):
    is_fileset = False
    is_field = False
    nested_types = ()

    @classmethod
    def type_var(cls, name):
        return SubtypeVar.new(name, cls)

    @classmethod
    def matches(cls, values) -> bool:
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
            cls(values)
        except FormatMismatchError:
            return False
        else:
            return True

    @classproperty
    def namespace(cls):
        """The "namespace" the format belongs to under the "fileformats" umbrella
        namespace"""
        module_parts = cls.__module__.split(".")
        if module_parts[0] != "fileformats":
            raise FileFormatsError(
                f"Cannot create reversible MIME type for {cls} as it is not in the "
                "fileformats namespace"
            )
        return module_parts[1].replace("_", "-")

    @classproperty
    def all_types(self):
        return itertools.chain(FileSet.all_formats, Field.all_fields)

    @classmethod
    def subclasses(cls):
        """Iterate over all installed subclasses"""
        for subpkg in subpackages():
            for attr_name in dir(subpkg):
                attr = getattr(subpkg, attr_name)
                if isclass(attr) and issubclass(attr, cls):
                    yield attr

    @classmethod
    def get_converter(cls, source_format: type, name: str = "converter", **kwargs):
        if issubclass(source_format, cls):
            return None
        else:
            raise FormatConversionError(
                f"Cannot converter between '{cls.mime_like}' and '{source_format.mime_like}'"
            )

    @classproperty
    def mime_like(cls):
        """Generates a "MIME-like" identifier from a format class (i.e.
        an identifier for a non-MIME class in the MIME style), e.g.

            fileformats.text.Plain to "text/plain"

        and

            fileformats.image.TiffFx to "image/tiff-fx"

        Parameters
        ----------
        klass : type(FileSet)
            FileSet subclass
        iana_mime : bool
            whether to use standardised IANA format or a more relaxed type format corresponding
            to the fileformats extension the type belongs to

        Returns
        -------
        type
            the corresponding file format class
        """
        return f"{cls.namespace}/{to_mime_format_name(cls.__name__)}"

    @classmethod
    def from_mime(cls, mime_string):
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
        try:
            namespace, format_name = mime_string.split("/")
        except ValueError:
            raise FormatRecognitionError(
                f"Format '{mime_string}' is not a valid MIME-like format of <namespace>/<format>"
            )
        else:
            namespace = namespace.replace("-", "_")
        # Attempt to load file type using their `iana_mime` attribute
        try:
            return FileSet.formats_by_iana_mime[mime_string]
        except KeyError:
            pass
        if namespace == "application" and format_name.startswith("x-"):
            # We treat the "application/x-" namespace as a catch-all for any formats
            # that are not explicitly covered by the IANA standard (which is how the IANA
            # treats it). Therefore, we loop through all subclasses across the different
            # namespaces to find one that matches the name.
            format_name = format_name[2:]  # remove "x-" prefix
            matching_name = FileSet.formats_by_name[format_name]
            matching_name = [
                m
                for m in matching_name
                if m.__module__ not in IANA_MIME_TYPE_REGISTRIES
            ]
            if not matching_name:
                namespace_names = [
                    p.__name__
                    for p in subpackages()
                    if p.__name__ not in IANA_MIME_TYPE_REGISTRIES
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
                    qualifier_names, classified_name = format_name.split("+")
                    try:
                        classifiers = [
                            getattr(module, from_mime_format_name(q))
                            for q in qualifier_names.split(".")
                        ]
                    except AttributeError:
                        raise FormatRecognitionError(
                            f"Could not load classifiers [{qualifier_names}] from "
                            f"fileformats.{namespace}, corresponding to MIME, "
                            f"or MIME-like, type {mime_string}"
                        ) from None
                    try:
                        classified = getattr(
                            module, from_mime_format_name(classified_name)
                        )
                    except AttributeError:
                        try:
                            classified = cls.generically_classifies_by_name[
                                classified_name
                            ]
                        except KeyError:
                            raise FormatRecognitionError(
                                f"Could not load classified class '{classified_name}' from "
                                f"fileformats.{namespace} or list of generic types "
                                f"({list(cls.generically_classifies_by_name)}), "
                                f"corresponding to MIME, or MIME-like, type {mime_string}"
                            ) from None
                    klass = classified[classifiers]
                else:
                    raise FormatRecognitionError(
                        f"Did not find '{class_name}' class in fileformats.{namespace} "
                        f"corresponding to MIME, or MIME-like, type {mime_string}"
                    ) from None
        return klass

    @classproperty
    def generically_classifies_by_name(cls):
        if cls._generically_classifies_by_name is None:
            cls._generically_classifies_by_name = {
                to_mime_format_name(f.__name__): f
                for f in FileSet.all_formats
                if getattr(f, "generically_classifies", False)
            }
        return cls._generically_classifies_by_name

    _generically_classifies_by_name = None  # Register all generically classified types

    REQUIRED_ANNOTATION = "__fileformats_required__"
    CHECK_ANNOTATION = "__fileformats_check__"


from .fileset import FileSet  # noqa
from .field import Field  # noqa
