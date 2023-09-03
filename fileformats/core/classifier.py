from .utils import classproperty


class Classifier:
    """Base class for all file-format "classifiers", including datatypes and abstract
    types"""

    @classproperty
    def _type_name(cls):
        """Name of type to be used in __repr__. Defined here so it can be overridden"""
        return cls.__name__

    @classproperty
    def category(cls):
        """The base classifier in the ontological root. There can only be one classifier
        in each category in a set of classifiers"""
        return [c for c in cls.__mro__ if issubclass(c, Classifier)][-1]
