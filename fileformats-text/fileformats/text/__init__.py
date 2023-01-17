from ._version import __version__
from warnings import warn
import json
import yaml
from fileformats.core import File
from fileformats.core import mark


# General formats
class Plain(File):
    ext = ".txt"


class Csv(File):
    ext = ".csv"


class Tsv(File):
    ext = ".tsv"


class Html(File):
    ext = ".html"
    alternate_exts = (".htm",)


class Xml(File):
    ext = ".xml"


class DataDictSerialization(File):
    "Base class for text-based hierarchical data-serialization formats, e.g. JSON, YAML"

    @mark.check
    def load(self):
        """Load the contents of the file into a dictionary"""
        raise NotImplementedError

    @classmethod
    def save_new(dct, fspath):
        """Serialise a dictionary to a new file"""
        raise NotImplementedError


class Json(DataDictSerialization):
    ext = ".json"

    def load(self):
        with open(self.fspath) as f:
            dct = json.load(f)
        return dct

    @classmethod
    def save_new(cls, dct, fspath):
        with open(fspath, "w") as f:
            json.dump(dct, f)
        return cls(fspath)


class Yaml(DataDictSerialization):
    ext = ".yaml"
    alternate_exts = (".yml",)

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
    warn(f"could not import converters for fileformats.{__name__}  module")
