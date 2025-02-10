import typing as ty
from .decorators import classproperty
from .exceptions import FormatDefinitionError


class Classifier:
    """Base class for all file-format "classifiers", including datatypes and abstract
    types"""

    @classproperty  # type: ignore[arg-type]
    def type_name(cls) -> str:
        """Name of type to be used in __repr__. Defined here so it can be overridden"""
        return cls.__name__  # type: ignore

    @classproperty  # type: ignore[arg-type]
    def namespace(cls) -> ty.Optional[str]:
        """The "namespace" the format belongs to under the "fileformats" umbrella
        namespace"""
        module_parts = cls.__module__.split(".")
        if module_parts[0] != "fileformats":
            raise FormatDefinitionError(
                f"Cannot create reversible MIME type for {cls} as it is not in the "
                "fileformats namespace"
            )
        return module_parts[1].replace("_", "-")

    def dummy(self) -> float:

        i: int = 0

        return i
