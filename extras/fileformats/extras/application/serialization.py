from pathlib import Path
import typing as ty
import tempfile
import yaml
import pydra.mark
import pydra.engine.specs
from fileformats.core import hook
from fileformats.application import DataSerialization, Json, Yaml


@hook.converter(target_format=Json, output_format=Json)
@hook.converter(target_format=Yaml, output_format=Yaml)
@pydra.mark.task
@pydra.mark.annotate({"return": {"out_file": DataSerialization}})
def convert_data_serialization(
    in_file: DataSerialization,
    output_format: ty.Type[DataSerialization],
    out_dir: ty.Optional[Path] = None,
):
    dct = in_file.load()
    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp())
    output_path = out_dir / (in_file.fspath.stem + output_format.ext)
    return output_format.save_new(output_path, dct)


@DataSerialization.load.register
def yaml_load(yml: Yaml) -> dict:
    with open(yml.fspath) as f:
        data = yaml.load(f, Loader=yaml.Loader)
    return data


@DataSerialization.save.register
def yaml_save(yml: Yaml, data: dict):
    with open(yml.fspath, "w") as f:
        yaml.dump(data, f)
