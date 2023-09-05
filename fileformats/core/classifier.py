import typing as ty
from .utils import classproperty


class Classifier:
    """Base class for all file-format "classifiers", including datatypes and abstract
    types"""

    @classproperty
    def type_name(cls):
        """Name of type to be used in __repr__. Defined here so it can be overridden"""
        return cls.__name__

    @classproperty
    def classifier_category(cls) -> "ty.Optional[ClassifierCategory]":
        """The base classifier in the ontological root. There can only be one classifier
        in each category in a set of classifiers"""
        if not issubclass(cls, ClassifierCategory):
            return None
        return [c for c in cls.__mro__[1:] if issubclass(c, ClassifierCategory)][-2]


class ClassifierCategory(Classifier):
    """Base class for classifier categories"""
