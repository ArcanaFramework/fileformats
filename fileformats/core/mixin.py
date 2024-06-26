from pathlib import Path
import re
import typing as ty
import logging
from . import hook
from .fileset import FileSet
from .utils import classproperty, describe_task, matching_source
from .identification import to_mime_format_name
from .converter import SubtypeVar
from .exceptions import (
    FormatMismatchError,
    FormatRecognitionError,
    FormatDefinitionError,
)


logger = logging.getLogger("fileformats")


class WithMagicNumber:
    """Mixin class for Files with magic numbers at the start of their
    contents.

    Class Attrs
    -----------
    magic_number : str or bytes
        the magic number/string to search for at the start of the file. If a unicode
        string then it is interpreted as the byte code in hex, if a bytes object, then
        it is treated as the byte string directly.
    binary : bool
        if the file-format is a binary type then this flag needs to be set in order to
        read the contents properly
    magic_number_offset : int, optional
        the offset in bytes from the start of the file that the magic number is stored
    """

    magic_number_offset = 0
    binary: bool
    magic_number: ty.Union[str, bytes]

    @hook.check
    def check_magic_number(self):
        if self.binary and isinstance(self.magic_number, str):
            magic_bytes = bytes.fromhex(self.magic_number)
        else:
            magic_bytes = self.magic_number
        read_magic_number = self.read_contents(
            len(magic_bytes), offset=self.magic_number_offset
        )
        if read_magic_number != magic_bytes:
            if self.binary and isinstance(self.magic_number, str):
                read_magic_str = '"' + bytes.hex(read_magic_number) + '"'
                magic_str = '"' + self.magic_number + '"'
            else:
                read_magic_str = read_magic_number
                magic_str = self.magic_number
            raise FormatMismatchError(
                f"Magic number of file {read_magic_str} doesn't match expected "
                f"{magic_str}"
            )


class WithMagicVersion:
    """Mixin class for Files with version numbers embedded within "magic numbers"
    the start of their contents.

    Class Attrs
    -----------
    magic_pattern : bytes
        the magic number/string to search for at the start of the file
    magic_pattern_offset : int, optional
        the offset in bytes from the start of the file that the magic pattern is read from
    magic_pattern_maxlength : int, optional
        the maximum length of the pattern, i.e. the length of the byte-string that will
        be read from the file, by default it will be the length of the magic_pattern
        string (which will probably be longer than the string it matches due to the
        special characters in the regex)
    """

    binary: bool
    magic_pattern: bytes
    magic_pattern_offset = 0
    magic_pattern_maxlength = None

    @hook.required
    @property
    def version(self) -> ty.Union[str, ty.Tuple[str]]:
        read_length = (
            self.magic_pattern_length
            if self.magic_pattern_length
            else len(self.magic_pattern)
        )
        read_bytes = self.read_contents(read_length, offset=self.magic_pattern_offset)
        match = re.match(self.magic_pattern, read_bytes)
        if not match:
            raise FormatMismatchError(
                f"Byte-string of length {read_length} at {self.magic_pattern_offset} "
                f"({read_bytes}), doesn't match expected pattern, {self.magic_pattern}"
            )
        version = tuple(b.decode("utf-8") for b in match.groups())
        if not version:
            raise FormatDefinitionError(
                f"No version patterns found in magic pattern of {type(self).__name__} "
                f"class, {self.magic_pattern}"
            )
        if len(version) == 1:
            version = version[0]
        return version


class WithAdjacentFiles:
    """
    If only the main fspath is provided to the __init__ of the class, this mixin
    automatically includes any "adjacent files", i.e. any files with the same stem but
    different extensions

    Note that WithAdjacentFiles must come before the primary type in the method-resolution
    order of the class so it can override the '_additional_paths' method in

        class MyFileFormatWithSeparateHeader(WithSeparateHeader, MyFileFormat):

            header_type = MyHeaderType
    """

    fspaths: ty.FrozenSet[Path]

    def _additional_fspaths(self):
        if len(self.fspaths) == 1:
            self.fspaths |= self.get_adjacent_files()
            trim = True
        else:
            trim = False
        if trim:
            self.trim_paths()

    def get_adjacent_files(self) -> ty.Set[Path]:
        stem = self.stem  # pylint: disable=no-member
        adjacents = set()
        for sibling in self.fspath.parent.iterdir():  # pylint: disable=no-member
            if (
                sibling != self.fspath  # pylint: disable=no-member
                and sibling.is_file()
                and sibling.name.startswith(stem + ".")
            ):
                adjacents.add(sibling)
        return adjacents


class WithSeparateHeader(WithAdjacentFiles):
    """Mixin class for Files with metadata stored in separate header files (typically
    with the same file stem but differing extension)

    Note that WithSeparateHeader must come before the primary type in the method-resolution
    order of the class so it can override the '__attrs_post_init__' method, e.g.

        class MyFileFormatWithSeparateHeader(WithSeparateHeader, MyFileFormat):

            header_type = MyHeaderType

    Class Attrs
    -----------
    header_type : type
        the file-format of the header file
    """

    @classproperty
    def nested_types(cls):
        return (cls.header_type,)

    @hook.required
    @property
    def header(self):
        return self.header_type(self.select_by_ext(self.header_type))

    def read_metadata(self):
        return self.header.load()


class WithSideCars(WithAdjacentFiles):
    """Mixin class for Files with a "side-car" file that augments the inline metadata
    (typically with the same file stem but differing extension).

    Note that WithSideCars must come before the primary type in the method-resolution
    order of the class so it can override the '__attrs_post_init__' and 'read_metadata'
    methods, e.g.

        class MyFileFormatWithSideCars(WithSideCars, MyFileFormat):

            primary_type = MyFileFormat
            side_car_types = (MySideCarType,)

    Class Attrs
    -----------
    primary_type : type
        the file-format of the primary file (used to read the inline metadata), can be
        the base class that implements 'read_metadata'
    side_car_types : tuple[type, ...]
        the file-formats of the expected side-car files
    """

    @hook.required
    @property
    def side_cars(self):
        return [tp(self.select_by_ext(tp)) for tp in self.side_car_types]

    def read_metadata(self):
        metadata = self.primary_type.read_metadata(self)
        for side_car in self.side_cars:
            try:
                side_car_metadata = side_car.load()
            except AttributeError:
                continue
            else:
                metadata[
                    to_mime_format_name(type(side_car).__name__)
                ] = side_car_metadata
        return metadata

    @classproperty
    def nested_types(cls):
        return cls.side_car_types


class WithClassifiers:
    """Mixin class for adding the ability to qualify the format class to designate the
    type of information stored within the format, e.g. ``DirectoryContaining[Png, Gif]`` for a
    directory containing PNG and GIF files, ``Zip[DataFile]`` for a zipped data file,
    ``Array[Integer]`` for an array containing integers, or DicomDir[T1w, Brain] for a
    T1-weighted MRI scan of the brain in DICOM format.

        class MyFormatWithClassifiers(WithClassifiers, File):

            ext = ".myf


        def my_func(file: MyFormatWithClassifiers[Integer]):
            ...

    A unique class will be returned (i.e. multiple calls with the same arguments will
    return the same class)

    Class Attrs
    -----------
    classifiers_attr_name : str, optional
        an attribute name to store the classifiers at within the classified class. This
        should be used if you need to reference the ``classifiers`` attribute directly
        in any validation/other methods (i.e. in most cases), to handle the case of
        diamond inheritance between two classes that can be classified.
        A default value should also be set in the unclassified base for this attribute,
        which is either ``()`` if ``multiple_classifiers`` is true and ``None`` otherwise
    <classifiers-attr-name> : tuple[type, ...] or None, optional
        pass a default value to the attribute referenced by 'classifiers_attr_name'
    multiple_classifiers : bool, optional
        whether or not multiple content types are permitted for the container type, True
    allowed_classifiers : tuple[type,...], optional
        the allowable types (+ subclasses) for the content types. If None all types
        are allowed
    ordered_classifiers : bool, optional
        whether the order of the content types is important or not, by default false
    genericly_classified : bool, optional
        whether the class can be classified by classifiers in any namespace (true) or just the
        namespace it belongs to (false). If true, then the namespace of the genericly
        classified class is omitted from the "mime-like" string. Note that the
        class' name therefore needs to be globally unique amongst all other genericly
        classified classes and so it should be used sparingly, i.e., highly generic
        formats that are unambiguous across all namespaces, such as "directory", "zip",
        "gzip", "json", "yaml", etc...
    """

    classifiers = ()  # classifiers set in the current class
    _classified_subtypes = {}
    # dict of previously created classified subtypes. If an existing class with matching
    # classifiers has been created it is returned instead of creating a new type. This
    # ensures that ``assert MyFormat[Qualifier] is MyFormat[Qualifier]``

    # Default values for class attrs
    multiple_classifiers = True
    allowed_classifiers: ty.Optional[ty.Tuple[ty.Type[ty.Any]]] = None
    exclusive_classifiers: ty.Tuple[ty.Type[ty.Any]] = ()
    ordered_classifiers = False
    generically_classifies = False

    def _validate_class(self):
        if self.wildcard_classifiers():
            raise FormatDefinitionError(
                f"Can instantiate {type(self)} class as it has wildcard classifiers "
                "and therefore should only be used for converter specifications"
            )

    @classproperty
    def is_classified(cls):  # pylint: disable=no-self-argument
        return "unclassified" in cls.__dict__

    @classproperty
    def nested_types(cls):
        return cls.classifiers

    @classmethod
    def wildcard_classifiers(cls, classifiers=None):
        if classifiers is None:
            classifiers = cls.classifiers if cls.is_classified else ()
        return frozenset(t for t in classifiers if issubclass(t, SubtypeVar))

    @classmethod
    def non_wildcard_classifiers(cls, classifiers=None):
        if classifiers is None:
            classifiers = cls.classifiers if cls.is_classified else ()
        return frozenset(q for q in classifiers if not issubclass(q, SubtypeVar))

    @classmethod
    def __class_getitem__(cls, classifiers):
        """Set the content types for a newly created dynamically type"""
        if isinstance(classifiers, ty.Iterable):
            classifiers = tuple(classifiers)
        else:
            classifiers = (classifiers,)
        if cls.allowed_classifiers:
            not_allowed = [
                q
                for q in classifiers
                if not any(issubclass(q, t) for t in cls.allowed_classifiers)
            ]
            if not_allowed:
                raise FormatDefinitionError(
                    f"Invalid content types provided to {cls} (must be subclasses of "
                    f"{cls.allowed_classifiers}): {not_allowed}"
                )
        # Sort content types if order isn't important
        if cls.multiple_classifiers:
            if not cls.ordered_classifiers:
                # Check for duplicate classifiers in the multiple list
                if len(classifiers) > 1:
                    # Sort the classifiers into categories and ensure that there aren't more
                    # than one type for each category. Otherwise, if the classifier doesn't
                    # belong to a category, check to see that there aren't multiple sub-classes
                    # in the classifier set
                    repetitions = {
                        c: [] for c in cls.exclusive_classifiers + classifiers
                    }
                    for classifier in classifiers:
                        for exc_classifier in repetitions:
                            if issubclass(classifier, exc_classifier):
                                repetitions[exc_classifier].append(classifier)
                    repeated = [t for t in repetitions.items() if len(t[1]) > 1]
                    if repeated:
                        raise FormatDefinitionError(
                            "Cannot have more than one occurrence of a classifier "
                            f"or subclasses for {cls} class when "
                            f"{cls.__name__}.ordered_classifiers is false:\n"
                            + "\n".join(
                                f"{k!r}: " + ", ".join(repr(x) for x in v)
                                for k, v in repeated
                            )
                        )
                classifiers = frozenset(classifiers)
        else:
            if len(classifiers) > 1:
                raise FormatDefinitionError(
                    f"Multiple classifiers not permitted for {cls} types, provided: "
                    f"({classifiers})"
                )
        # Make sure that the "classified" dictionary is present in this class not super
        # classes
        if "_classified_subtypes" not in cls.__dict__:
            cls._classified_subtypes = {}
        try:
            # Load previously created type so we can do ``assert MyType[Integer] is MyType[Integer]``
            classified = cls._classified_subtypes[classifiers]
        except KeyError:
            if not hasattr(cls, "classifiers_attr_name"):
                raise FormatDefinitionError(
                    f"{cls} needs to define the 'classifiers_attr_name' class attribute "
                    "with the name of the (different) class attribute to hold the "
                    "classified types"
                )
            if cls.classifiers_attr_name is None:
                raise FormatDefinitionError(
                    f"Inherited classifiers have been disabled in {cls} (by setting "
                    f'"classifiers_attr_name)" to None)'
                )
            try:
                classifiers_attr = getattr(cls, cls.classifiers_attr_name)
            except AttributeError:
                raise FormatDefinitionError(
                    f"Default value for classifiers attribute "
                    f"'{cls.classifiers_attr_name}' needs to be set in {cls}"
                )
            else:
                if classifiers_attr:
                    raise FormatDefinitionError(
                        f"Default value for classifiers attribute "
                        f"'{cls.classifiers_attr_name}' needs to be set in {cls}"
                    )
            class_attrs = {
                "unclassified": cls,
                "classifiers": classifiers,
            }
            class_attrs[cls.classifiers_attr_name] = (
                classifiers if cls.multiple_classifiers else classifiers[0]
            )
            classifier_names = [t.__name__ for t in classifiers]
            if not cls.ordered_classifiers:
                classifier_names.sort()
            classified = type(
                f"{'_'.join(classifier_names)}__{cls.__name__}",
                (cls,),
                class_attrs,
            )
            classified.__module__ = cls.__module__
            cls._classified_subtypes[classifiers] = classified
        return classified

    @classmethod
    def get_converter_tuples(
        cls, source_format: type
    ) -> ty.List[ty.Tuple[ty.Callable, ty.Dict[str, ty.Any]]]:
        """Search the registered converters to find an appropriate task and associated
        key-word args to perform the conversion between source and target formats

        Parameters
        ----------
        source_format : type(FileSet)
            the source format to convert from
        """
        # Try to see if a converter has been defined to the exact type
        available_converters = super().get_converter_tuples(
            source_format
        )  # pylint: disable=no-member
        # Failing that, see if there is a generic conversion between the container type
        # the source format (or subclass of) defined with matching wildcards in the source
        # and target formats
        if not available_converters and cls.is_classified:
            converters_dict = FileSet.get_converters_dict(
                cls.unclassified
            )  # pylint: disable=no-member
            for template_source_format, converter in converters_dict.items():
                if len(converter) == 3:  # was defined with wildcard classifiers
                    converter, conv_kwargs, template_classifiers = converter
                    # Attempt conversion from generic type to template match
                    if issubclass(template_source_format, SubtypeVar):
                        assert tuple(
                            cls.wildcard_classifiers(template_classifiers)
                        ) == (template_source_format,)
                        non_wildcards = cls.non_wildcard_classifiers(
                            template_classifiers
                        )
                        to_match = tuple(set(cls.classifiers).difference(non_wildcards))
                        if len(to_match) > 1:
                            wildcard_match = False
                        else:
                            wildcard_match = issubclass(source_format, to_match[0])
                    # Attempt template to template conversion match
                    elif getattr(source_format, "is_classified", False) and issubclass(
                        source_format.unclassified, template_source_format.unclassified
                    ):
                        assert cls.wildcard_classifiers(
                            template_classifiers
                        ) == cls.wildcard_classifiers(
                            template_source_format.classifiers
                        )
                        if cls.ordered_classifiers:
                            if len(cls.classifiers) != len(template_classifiers) or len(
                                source_format.classifiers
                            ) != len(template_source_format.classifiers):
                                wildcard_match = False
                            else:
                                wildcard_map = {}
                                for actual, template in zip(
                                    source_format.classifiers,
                                    template_source_format.classifiers,
                                ):
                                    if issubclass(template, SubtypeVar):
                                        wildcard_map[template] = actual
                                wildcard_match = True
                                for actual, template in zip(
                                    cls.classifiers, template_classifiers
                                ):
                                    if issubclass(template, SubtypeVar):
                                        try:
                                            reference = wildcard_map[template]
                                        except KeyError:
                                            wildcard_match = False
                                            break
                                        else:
                                            if not issubclass(actual, reference):
                                                wildcard_match = False
                                                break
                                    elif not issubclass(actual, template):
                                        wildcard_match = False
                                        break
                        else:
                            non_wildcards = cls.non_wildcard_classifiers(
                                template_classifiers
                            )
                            src_non_wildcards = cls.non_wildcard_classifiers(
                                template_source_format.classifiers
                            )
                            if not non_wildcards.issubset(
                                set(cls.classifiers)
                            ) or not src_non_wildcards.issubset(
                                set(source_format.classifiers)
                            ):
                                wildcard_match = False
                            else:
                                to_match = set(cls.classifiers).difference(
                                    non_wildcards
                                )
                                from_types = set(source_format.classifiers).difference(
                                    src_non_wildcards
                                )
                                wildcard_match = to_match.issubset(from_types)
                    else:
                        wildcard_match = False
                    if wildcard_match:
                        available_converters.append((converter, conv_kwargs))
        return available_converters

    @classmethod
    def __subclasshook__(cls, subclass: type) -> bool:
        """Overload the behaviour of 'issubclass' so that classified classes are considered
        to be subclasses of each other if they contain a super-set of classifiers"""
        if type.__subclasscheck__(cls, subclass):
            return True
        # Check to see whether the unclassified types are equivalent
        if (
            not cls.is_classified
            or not getattr(subclass, "is_classified", False)
            or not issubclass(subclass.unclassified, cls.unclassified)
        ):
            return False
        if cls.ordered_classifiers:
            assert subclass.ordered_classifiers
            if len(subclass.classifiers) != len(cls.classifiers):
                is_subclass = False
            else:
                is_subclass = all(
                    issubclass(q, s)
                    for q, s in zip(subclass.classifiers, cls.classifiers)
                )
        else:
            assert not subclass.ordered_classifiers
            if subclass.classifiers.issuperset(cls.classifiers):
                is_subclass = True
            else:
                # Check for sub-classes of classifiers
                is_subclass = all(
                    any(issubclass(q, s) for q in subclass.classifiers)
                    for s in cls.classifiers
                )
        return is_subclass

    @classmethod
    def register_converter(
        cls,
        source_format: type,
        converter_tuple: ty.Tuple[ty.Callable, ty.Dict[str, ty.Any]],
    ):
        """Registers a converter task within a class attribute. Called by the @fileformats.hook.converter
        decorator.

        Parameters
        ----------
        source_format : type
            the source format to register a converter from
        converter_tuple
            a tuple consisting of a `task_spec` callable that resolves to a Pydra task
            and a dictionary of keyword arguments to be passed to the task spec at
            initialisation time

        Raises
        ------
        FormatConversionError
            if there is already a converter registered between the two types
        """
        # Ensure "converters" dict is defined in the target class and not in a superclass
        if cls.wildcard_classifiers():
            if issubclass(source_format, SubtypeVar):
                if len(cls.wildcard_classifiers()) > 1:
                    raise FormatDefinitionError(
                        "Can only have one wildcard qualifier when registering a converter "
                        f"to {cls} from a generic type, found {cls.wildcard_classifiers()}"
                    )
            elif not source_format.is_classified:
                raise FormatDefinitionError(
                    "Can only use wildcard classifiers when registering a converter "
                    f"from a generic type or similarly classified type, not {source_format}"
                )
            else:
                if cls.wildcard_classifiers() != source_format.wildcard_classifiers():
                    raise FormatDefinitionError(
                        f"Mismatching wildcards between source format, {source_format} "
                        f"({list(source_format.wildcard_classifiers())}), and target "
                        f"{cls} ({cls.wildcard_classifiers()})"
                    )
                prev_registered = [
                    f
                    for f in cls.converters
                    if (
                        issubclass(source_format.unclassified, f.unclassified)
                        and f.non_wildcard_classifiers()
                        == source_format.non_wildcard_classifiers()
                    )
                ]
                assert len(prev_registered) <= 1
                prev = prev_registered[0] if prev_registered else None
                if prev:
                    prev_tuple = cls.converters[prev]
                    task, task_kwargs = converter_tuple
                    prev_task, prev_kwargs, prev_classifiers = prev_tuple
                    if (
                        matching_source(task, prev_task)
                        and task_kwargs == prev_kwargs
                        and cls.classifiers == prev_classifiers
                    ):
                        logger.warning(
                            "Ignoring duplicate registrations of the same converter %s",
                            describe_task(task),
                        )
                        return  # actually the same task but just imported twice for some reason
                    raise FormatDefinitionError(
                        f"Cannot register converter from {prev.unclassified} "
                        f"to {cls.unclassified} with non-wildcard classifiers "
                        f"{list(prev.non_wildcard_classifiers())}, {describe_task(task)}, "
                        f"because there is already one registered, {describe_task(prev_task)}"
                    )
            converters_dict = cls.unclassified.get_converters_dict()
            converters_dict[source_format] = converter_tuple + (cls.classifiers,)
        else:
            super().register_converter(source_format, converter_tuple)

    @classproperty
    def namespace(cls):  # pylint: disable=no-self-argument
        """The "namespace" the format belongs to under the "fileformats" umbrella
        namespace"""
        if cls.is_classified:
            namespaces = set(t.namespace for t in cls.classifiers)
            if not cls.generically_classifies:
                namespaces.add(cls.unclassified.namespace)
            if len(namespaces) == 1:
                return next(iter(namespaces))
            else:
                # Handle subpackage namespaces and parent, e.g. medimage & medimage-fsl
                namespaces = sorted(namespaces)
                if (
                    len(namespaces) == 2
                    and namespaces[1].split("-")[0] == namespaces[0]
                ):
                    return namespaces[1]
                msg = (
                    "Cannot create reversible MIME type for because did not find a "
                    f"common namespace between all classifiers {list(cls.classifiers)}"
                )
                if not cls.generically_classifies:
                    msg += (
                        f" and (non genericly classified) base class {cls.unclassified}"
                    )
                raise FormatRecognitionError(msg + f", found:\n{list(namespaces)}")
        else:
            namespace = super().namespace
        return namespace

    @classproperty
    def type_name(cls):
        """Name of type including classifiers to be used in __repr__"""
        if cls.is_classified:
            unclassified = cls.unclassified.__name__
        else:
            unclassified = type(cls).__name__
        return (
            unclassified + "[" + ", ".join(t.type_name for t in cls.classifiers) + "]"
        )
