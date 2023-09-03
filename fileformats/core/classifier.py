from .utils import classproperty


class ClassifierCategory:
    """Base class for categories of classifiers. When used in a WithClassifier mixin"""


class Classifier:
    """Base class for all file-format "classifiers", including datatypes and abstract
    types"""

    @classproperty
    def _type_name(cls):
        """Name of type to be used in __repr__. Defined here so it can be overridden"""
        return cls.__name__
