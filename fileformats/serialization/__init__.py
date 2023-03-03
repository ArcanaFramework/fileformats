from pathlib import Path
import json
from ..core import __version__, mark, DataType
from ..core.mixin import WithQualifiers
from ..generic import File
from ..core.utils import MissingExtendedDependency

try:
    import yaml
except ImportError:
    yaml = MissingExtendedDependency("yaml", __name__)


class Schema(DataType):
    """Base class for all serialization schemas (can be used for abstract schemas that
    don't actually have a formal definition)"""

    pass


class JsonSchema(Schema):
    pass


class XmlSchema(Schema):
    pass


class InformalSchema(Schema):
    "Not actually a strict schema, just a set of conventions on how to structure the serialization"


class DataSerialization(WithQualifiers, File):
    "Base class for text-based hierarchical data-serialization formats, e.g. JSON, YAML"

    # Qualifiers class attrs
    qualifiers_attr_name = "schema"
    schema = None
    multiple_qualifiers = False
    allowed_qualifiers = (Schema,)
    generically_qualifies = True

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
    allowed_qualifiers = (XmlSchema, InformalSchema)


class Json(DataSerialization):
    ext = ".json"
    allowed_qualifiers = (JsonSchema, InformalSchema)

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
