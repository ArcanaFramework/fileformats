from __future__ import annotations
from inspect import isclass
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
    add_exc_note,
    from_mime_format_name,
)


class DataType:
    is_fileset = False
    is_field = False

    @classmethod
    def type_var(cls, name):
        return SubtypeVar(name, cls)

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

    @classmethod
    def issubtype(cls, super_type: type, allow_same: bool = True):
        """Check to see whether datatype class is a subtype of a given super class.
        In this case the subtype is expected to be able to be treated as if it was
        the super class.

        Overridden in the ``WithClassifiers`` mixin to add support for
        classified subtypes

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
        if allow_same and cls is super_type:
            return True
        if isinstance(super_type, SubtypeVar):
            super_type = super_type.base
        return issubclass(cls, super_type)

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
        return module_parts[1]

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
        if source_format.issubtype(cls):
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
        mime = f"{cls.namespace}/{to_mime_format_name(cls.__name__)}"
        try:
            cls.from_mime(mime)
        except FormatRecognitionError as e:
            add_exc_note(
                e,
                (
                    f"Cannot create reversible MIME type for {cls} as it is not present "
                    f"in a top-level fileformats namespace package '{cls.namespace}'"
                ),
            )
            raise e
        return mime

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
        try:
            return FileSet.formats_by_iana_mime[mime_string]
        except KeyError:
            pass
        if namespace == "application":
            # We treat the "application" namespace as a catch-all for any formats that are
            # not explicitly covered by the IANA standard (which is kind of how the IANA
            # treats it). Therefore, we loop through all subclasses across the different
            # namespaces to find one that matches the name.
            if not format_name.startswith("x-"):
                raise FormatRecognitionError(
                    "Did not find class matching official (i.e. non-extension) MIME type "
                    f"{mime_string} (i.e. one not starting with 'application/x-'"
                ) from None
            format_name = format_name[2:]  # remove "x-" prefix
            matching_name = FileSet.formats_by_name[format_name]
            if not matching_name:
                namespace_names = [n.__name__ for n in subpackages()]
                class_name = from_mime_format_name(format_name)
                raise FormatRecognitionError(
                    f"Did not find class matching extension the class name '{class_name}' "
                    f"corresponding to MIME type '{mime_string}' "
                    f"in any of the installed namespaces: {namespace_names}"
                )
            elif len(matching_name) > 1:
                namespace_names = [f.__module__.__name__ for f in matching_name]
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
                            classified = cls.generically_qualifies_by_name[
                                classified_name
                            ]
                        except KeyError:
                            raise FormatRecognitionError(
                                f"Could not load classified class '{classified_name}' from "
                                f"fileformats.{namespace} or list of generic types "
                                f"({list(cls.generically_qualifies_by_name)}), "
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
    def generically_qualifies_by_name(cls):
        if cls._generically_qualifies_by_name is None:
            cls._generically_qualifies_by_name = {
                to_mime_format_name(f.__name__): f
                for f in FileSet.all_formats
                if getattr(f, "generically_qualifies", False)
            }
        return cls._generically_qualifies_by_name

    _generically_qualifies_by_name = None  # Register all generically classified types


from .fileset import FileSet  # noqa
from .field import Field  # noqa
