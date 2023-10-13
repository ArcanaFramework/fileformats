import json
import typing as ty
from random import Random
from pathlib import Path
from ..core import mark, DataType
from ..core.mixin import WithClassifiers
from ..generic import File
from ..core.exceptions import FormatMismatchError
from ..core.utils import gen_filename


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


class DataSerialization(WithClassifiers, File):
    "Base class for text-based hierarchical data-serialization formats, e.g. JSON, YAML"

    # Classifiers class attrs
    classifiers_attr_name = "schema"
    schema = None
    multiple_classifiers = False
    allowed_classifiers = (Schema,)
    generically_qualifies = True
    binary = False

    iana_mime = None

    @mark.extra
    def load(self):
        """Load the contents of the file into a dictionary"""
        raise NotImplementedError

    @mark.extra
    def save(data):
        """Serialise a dictionary to a new file"""
        raise NotImplementedError

    @classmethod
    def save_new(cls, fspath, data):
        # We have to use a mock object as the data file hasn't been written yet
        mock = cls.mock(fspath)
        mock.save(data)
        return cls(fspath)


class Xml(DataSerialization):
    ext = ".xml"
    allowed_classifiers = (XmlSchema, InformalSchema)


class Json(DataSerialization):
    ext = ".json"
    allowed_classifiers = (JsonSchema, InformalSchema)

    @mark.check
    def load(self):
        try:
            with open(self.fspath) as f:
                dct = json.load(f)
        except json.JSONDecodeError as e:
            raise FormatMismatchError(
                f"'{self.fspath}' is not a valid JSON file"
            ) from e
        return dct

    def save(self, data):
        with open(self.fspath, "w") as f:
            json.dump(data, f)


class Yaml(DataSerialization):
    ext = ".yaml"
    alternate_exts = (".yml",)


class Toml(DataSerialization):
    ext = ".toml"


@File.generate_sample_data.register
def generate_json_sample_data(
    js: Json, dest_dir: Path, seed: int, stem: ty.Optional[str]
) -> ty.List[Path]:
    js_file = dest_dir / gen_filename(seed, file_type=js, stem=stem)
    rng = Random(seed + 1)
    with open(js_file, "w") as f:
        json.dump(
            {"a": True, "b": "two", "c": 3, "d": [rng.randint(0, 10), rng.random(), 6]},
            f,
        )
    return [js_file]


@File.generate_sample_data.register
def generate_yaml_sample_data(
    yml: Yaml, dest_dir: Path, seed: int, stem: ty.Optional[str]
) -> ty.List[Path]:
    yml_file = dest_dir / gen_filename(seed, file_type=yml, stem=stem)
    rng = Random(seed + 1)
    with open(yml_file, "w") as f:
        f.write(
            f"""# Generated sample YAML file by FileFormats
a: True
b: two
c: 3
d:
- {rng.randint(0, 10)}
- {rng.random()}
- 6
"""
        )
    return [yml_file]
