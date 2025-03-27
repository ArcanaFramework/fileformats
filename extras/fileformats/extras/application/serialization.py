from pathlib import Path
import typing as ty
import tempfile
import yaml
from pydra.compose import python
from fileformats.core import FileSet, converter, extra_implementation
from fileformats.application import TextSerialization, Json, Yaml
from fileformats.application.serialization import SerializationType


@converter(target_format=Json, output_format=Json)  # type: ignore[misc]
@converter(target_format=Yaml, output_format=Yaml)  # type: ignore[misc]
@python.define(outputs={"out_file": TextSerialization})  # type: ignore[misc]
def convert_data_serialization(
    in_file: TextSerialization,
    output_format: ty.Type[TextSerialization],
    out_dir: ty.Optional[Path] = None,
) -> TextSerialization:
    dct = in_file.load()
    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp())
    output_path = out_dir / (
        in_file.fspath.stem + (output_format.ext if output_format.ext else "")
    )
    return output_format.new(output_path, dct)


@extra_implementation(FileSet.load)
def yaml_load(yml: Yaml, **kwargs: ty.Any) -> SerializationType:
    with open(yml.fspath) as f:
        data = yaml.load(f, Loader=yaml.Loader)
    return data  # type: ignore[no-any-return]


@extra_implementation(FileSet.save)
def yaml_save(
    yml: Yaml,
    data: SerializationType,
    **kwargs: ty.Any,
) -> None:
    with open(yml.fspath, "w") as f:
        yaml.dump(data, f, **kwargs)
