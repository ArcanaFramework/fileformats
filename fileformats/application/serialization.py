import json
import typing as ty
from fileformats.core.typing import TypeAlias
from pathlib import Path
from fileformats.core import DataType, FileSet, extra_implementation
from fileformats.core.mixin import WithClassifier
from fileformats.generic import UnicodeFile
from fileformats.core.exceptions import FormatMismatchError
from fileformats.core import SampleFileGenerator


SerializationType: TypeAlias = ty.Union[ty.Dict[str, ty.Any], ty.List[ty.Any]]


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


class TextSerialization(WithClassifier, UnicodeFile):
    "Base class for text-based hierarchical data-serialization formats, e.g. JSON, YAML"

    # Classifiers class attrs
    classifiers_attr_name: ty.Optional[str] = "schema"
    schema: ty.Optional[ty.Type[Schema]] = None
    allowed_classifiers: ty.Tuple[ty.Type[Schema], ...] = (Schema,)
    generically_classifiable: bool = True


class Xml(TextSerialization):
    ext: ty.Optional[str] = ".xml"
    allowed_classifiers = (XmlSchema, InformalSchema)


class Json(TextSerialization):
    ext: ty.Optional[str] = ".json"
    allowed_classifiers = (JsonSchema, InformalSchema)

    # TODO: add validation mechanisms to check class


class Yaml(TextSerialization):
    ext = ".yaml"
    alternate_exts = (".yml",)


class Toml(TextSerialization):
    ext = ".toml"


@extra_implementation(FileSet.generate_sample_data)
def generate_json_sample_data(
    js: Json,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    js_file = generator.generate_fspath(file_type=Json)
    with open(js_file, "w") as f:
        json.dump(
            {
                "a": True,
                "b": "two",
                "c": 3,
                "d": [generator.rng.randint(0, 10), generator.rng.random(), 6],
            },
            f,
        )
    return [js_file]


@extra_implementation(FileSet.generate_sample_data)
def generate_yaml_sample_data(
    yml: Yaml,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    yml_file = generator.generate_fspath(file_type=Yaml)
    with open(yml_file, "w") as f:
        f.write(
            f"""# Generated sample YAML file by FileFormats
a: True
b: two
c: 3
d:
- {generator.rng.randint(0, 10)}
- {generator.rng.random()}
- 6
"""
        )
    return [yml_file]


@extra_implementation(FileSet.load)
def load(jsn: Json, **kwargs: ty.Any) -> SerializationType:
    try:
        with jsn.open() as f:
            dct: ty.Dict[str, ty.Any] = json.load(f, **kwargs)
    except json.JSONDecodeError as e:
        raise FormatMismatchError(f"'{jsn.fspath}' is not a valid JSON file") from e
    return dct


@extra_implementation(FileSet.save)
def save(jsn: Json, data: SerializationType, **kwargs: ty.Any) -> None:
    with jsn.open("w") as f:
        json.dump(data, f, **kwargs)
