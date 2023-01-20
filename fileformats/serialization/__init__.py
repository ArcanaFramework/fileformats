from warnings import warn
import json
from ..core import __version__, mark
from ..generic import File
from ..core.utils import MissingDependencyPlacholder

try:
    import yaml
except ImportError:
    yaml = MissingDependencyPlacholder("yaml", __name__)


class Serialization(File):
    "Base class for text-based hierarchical data-serialization formats, e.g. JSON, YAML"

    iana_mime = None

    @mark.check
    def load(self):
        """Load the contents of the file into a dictionary"""
        raise NotImplementedError

    @classmethod
    def save_new(dct, fspath):
        """Serialise a dictionary to a new file"""
        raise NotImplementedError


class Xml(Serialization):
    ext = ".xml"


class Json(Serialization):
    ext = ".json"

    @mark.check
    def load(self):
        with open(self.fspath) as f:
            dct = json.load(f)
        return dct

    @classmethod
    def save_new(cls, dct, fspath):
        with open(fspath, "w") as f:
            json.dump(dct, f)
        return cls(fspath)


class Yaml(Serialization):
    ext = ".yaml"
    alternate_exts = (".yml",)

    @mark.check
    def load(self):
        with open(self.fspath) as f:
            dct = yaml.load(f, Loader=yaml.Loader)
        return dct

    @classmethod
    def save_new(cls, dct, fspath):
        with open(fspath, "w") as f:
            yaml.dump(dct, f)
        return cls(fspath)


try:
    from .converters import *
except ImportError:
    f"could not import converters for {__name__}  module, please install with the"
    f"'extended' install extra to use converters for {__name__}, i.e.\n\n"
    "$ python3 -m pip install fileformats-medimage[extended]"
