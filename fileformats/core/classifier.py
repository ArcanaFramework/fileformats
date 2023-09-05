import typing as ty
from .utils import classproperty


class ClassifierCategory:
    """Base class for classifier categories. Only one member of each category is permitted
    in args for classified classes"""

    @classproperty
    def type_name(cls):
        """Name of type to be used in __repr__. Defined here so it can be overridden"""
        return cls.__name__


class Classifier:
    """Base class for all file-format "classifiers", including datatypes and abstract
    types"""

    classifier_category: ty.Optional[ClassifierCategory] = None

    @classproperty
    def type_name(cls):
        """Name of type to be used in __repr__. Defined here so it can be overridden"""
        return cls.__name__
