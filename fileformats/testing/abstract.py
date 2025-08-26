import typing as ty
from abc import abstractproperty
from pathlib import Path
from fileformats.generic import File
from fileformats.core import converter


class AbstractFile(File):
    """Base class for all medical imaging data including pre-image raw data and
    associated data"""

    @abstractproperty
    def a_property(self):
        raise NotImplementedError


class AbstractSubclass(AbstractFile):
    pass


class ConcreteClass(AbstractFile):

    @property
    def a_property(self):
        return "Concrete implementation of a_property"


class AnotherConcreteClass(AbstractSubclass):

    @property
    def a_property(self):
        return "Another concrete implementation of a_property"


class ConvertibleToFile(File):
    """A class that can be converted from a file"""

    pass
