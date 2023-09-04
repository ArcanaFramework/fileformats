from .utils import classproperty
from .exceptions import FileFormatsError


class ClassifierCategory:
    """Base class for classifier categories. Only one member of each category is permitted
    in args for classified classes"""


class Classifier:
    """Base class for all file-format "classifiers", including datatypes and abstract
    types"""

    @classproperty
    def _type_name(cls):
        """Name of type to be used in __repr__. Defined here so it can be overridden"""
        return cls.__name__

    @classproperty
    def classifier_category(cls) -> "ClassifierCategory":
        """The base classifier in the ontological root. There can only be one classifier
        in each category in a set of classifiers"""
        categories = [c for c in cls.__mro__ if issubclass(c, ClassifierCategory)]
        if len(categories) > 1:
            raise FileFormatsError(
                f"Classifier {cls} cannot inherit from multiple categories ({categories})"
            )
        if not categories:
            return None
        return categories[0]
