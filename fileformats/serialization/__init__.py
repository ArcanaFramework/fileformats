from pathlib import Path
import json
from ..core import __version__, mark
from ..generic import File
from ..core.utils import MissingExtendedDependency, import_converters

try:
    import yaml
except ImportError:
    yaml = MissingExtendedDependency("yaml", __name__)


class DataSerialization(File):
    "Base class for text-based hierarchical data-serialization formats, e.g. JSON, YAML"

    iana_mime = None

    @mark.check
    def load(self):
        """Load the contents of the file into a dictionary"""
        raise NotImplementedError

    @classmethod
    def save_new(fspath: Path, dct: dict):
        """Serialise a dictionary to a new file"""
        raise NotImplementedError


class Xml(DataSerialization):
    ext = ".xml"


class Json(DataSerialization):
    ext = ".json"

    @mark.check
    def load(self):
        with open(self.fspath) as f:
            dct = json.load(f)
        return dct

    @classmethod
    def save_new(cls, fspath, dct):
        with open(fspath, "w") as f:
            json.dump(dct, f)
        return cls(fspath)


class Yaml(DataSerialization):
    ext = ".yaml"
    alternate_exts = (".yml",)

    @mark.check
    def load(self):
        with open(self.fspath) as f:
            dct = yaml.load(f, Loader=yaml.Loader)
        return dct

    @classmethod
    def save_new(cls, fspath, dct):
        with open(fspath, "w") as f:
            yaml.dump(dct, f)
        return cls(fspath)


import_converters(__name__)
