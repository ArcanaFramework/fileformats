from pathlib import Path
import typing as ty
import tempfile
import yaml
import pydra.mark
import pydra.engine.specs
from fileformats.core import converter, extra_implementation
from fileformats.application import DataSerialization, Json, Yaml
from fileformats.application.serialization import LoadedSerialization


@converter(target_format=Json, output_format=Json)
@converter(target_format=Yaml, output_format=Yaml)
@pydra.mark.task  # type: ignore[misc]
@pydra.mark.annotate({"return": {"out_file": DataSerialization}})  # type: ignore[misc]
def convert_data_serialization(
    in_file: DataSerialization,
    output_format: ty.Type[DataSerialization],
    out_dir: ty.Optional[Path] = None,
) -> DataSerialization:
    dct = in_file.load()
    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp())
    output_path = out_dir / (
        in_file.fspath.stem + (output_format.ext if output_format.ext else "")
    )
    return output_format.save_new(output_path, dct)  # type: ignore[no-any-return]


@extra_implementation(DataSerialization.load)
def yaml_load(yml: Yaml) -> LoadedSerialization:
    with open(yml.fspath) as f:
        data = yaml.load(f, Loader=yaml.Loader)
    return data  # type: ignore[no-any-return]


@extra_implementation(DataSerialization.save)
def yaml_save(yml: Yaml, data: LoadedSerialization) -> None:
    with open(yml.fspath, "w") as f:
        yaml.dump(data, f)
