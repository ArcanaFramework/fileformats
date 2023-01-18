from pathlib import Path
import tempfile
import pydra.mark
import pydra.engine.specs
from fileformats.core import mark
from . import Serialization, Json, Yaml


@mark.converter(target_format=Json, output_format=Json)
@mark.converter(target_format=Yaml, output_format=Yaml)
@pydra.mark.task
@pydra.mark.annotate({"return": {"out_file": Serialization}})
def convert_data_serialization(
    in_file: Serialization, output_format: type, out_dir: Path = None
):
    dct = in_file.load()
    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp())
    output_path = out_dir / (in_file.fspath.stem + output_format.ext)
    return output_format.save_new(dct, output_path)
