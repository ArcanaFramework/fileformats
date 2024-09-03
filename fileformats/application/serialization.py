import json
import typing as ty
from typing_extensions import Self, TypeAlias
from pathlib import Path
from fileformats.core import extra, DataType, FileSet
from fileformats.core.mixin import WithClassifiers
from ..generic import File
from fileformats.core.exceptions import FormatMismatchError
from fileformats.core import SampleFileGenerator


LoadedSerialization: TypeAlias = ty.Union[ty.Dict[str, ty.Any], ty.List[ty.Any]]


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
    classifiers_attr_name: ty.Optional[str] = "schema"
    schema: ty.Optional[ty.Type[Schema]] = None
    multiple_classifiers: bool = False
    allowed_classifiers: ty.Tuple[ty.Type[Schema], ...] = (Schema,)
    generically_classifiable: bool = True
    binary: bool = False

    iana_mime: ty.Optional[str] = None

    @extra
    def load(self) -> LoadedSerialization:
        """Load the contents of the file into a dictionary"""
        raise NotImplementedError

    @extra
    def save(self, data: LoadedSerialization) -> None:
        """Serialise a dictionary to a new file"""
        raise NotImplementedError

    @classmethod
    def save_new(cls, fspath: ty.Union[str, Path], data: LoadedSerialization) -> Self:
        # We have to use a mock object as the data file hasn't been written yet
        mock = cls.mock(fspath)
        mock.save(data)
        return cls(fspath)


class Xml(DataSerialization):
    ext: ty.Optional[str] = ".xml"
    allowed_classifiers = (XmlSchema, InformalSchema)


class Json(DataSerialization):
    ext: ty.Optional[str] = ".json"
    allowed_classifiers = (JsonSchema, InformalSchema)

    def load(self) -> LoadedSerialization:
        try:
            with open(self.fspath) as f:
                dct: ty.Dict[str, ty.Any] = json.load(f)
        except json.JSONDecodeError as e:
            raise FormatMismatchError(
                f"'{self.fspath}' is not a valid JSON file"
            ) from e
        return dct

    def save(self, data: LoadedSerialization) -> None:
        with open(self.fspath, "w") as f:
            json.dump(data, f)


class Yaml(DataSerialization):
    ext = ".yaml"
    alternate_exts = (".yml",)


class Toml(DataSerialization):
    ext = ".toml"


@FileSet.generate_sample_data.register
def generate_json_sample_data(
    js: Json,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
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


@FileSet.generate_sample_data.register
def generate_yaml_sample_data(
    yml: Yaml,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
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
