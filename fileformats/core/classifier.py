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
                f"Cannot determine namespace for {cls} format as it is not in the "
                "fileformats namespace package"
            )
        namespace = module_parts[1]
        if namespace == "vendor":
            if len(module_parts) < 4:
                raise FormatDefinitionError(
                    f"Cannot determine namespace for vendor-specific format, {cls} it needs "
                    "to be in a subpackage of the form `fileformats.vendor.<vendor-name>.<namespace>`,"
                    f"found `{'.'.join(module_parts)}`"
                )
            namespace = module_parts[3]
        return namespace.replace("_", "-")

    @classproperty
    def vendor(cls) -> ty.Optional[str]:
        module_parts = cls.__module__.split(".")
        if module_parts[0] != "fileformats" or module_parts[1] != "vendor":
            return None
        return module_parts[2].replace("_", "-")

    def dummy(self) -> float:

        i: int = 0

        return i
