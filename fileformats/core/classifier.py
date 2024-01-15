from .utils import classproperty


class Classifier:
    """Base class for all file-format "classifiers", including datatypes and abstract
    types"""

    @classproperty
    def type_name(cls):
        """Name of type to be used in __repr__. Defined here so it can be overridden"""
        return cls.__name__
