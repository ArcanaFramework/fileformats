from pathlib import Path
import tempfile
import pydra.mark
import pydra.engine.specs
from fileformats.core import mark
from .raster import RasterImage, Bitmap, Gif, Jpeg, Png, Tiff


@mark.converter(target_format=Bitmap, output_format=Bitmap)
@mark.converter(target_format=Gif, output_format=Gif)
@mark.converter(target_format=Jpeg, output_format=Jpeg)
@mark.converter(target_format=Png, output_format=Png)
@mark.converter(target_format=Tiff, output_format=Tiff)
@pydra.mark.task
@pydra.mark.annotate({"return": {"out_file": RasterImage}})
def convert_image(in_file: RasterImage, output_format: type, out_dir: Path = None):
    data_array = in_file.load()
    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp())
    output_path = out_dir / (in_file.fspath.stem + output_format.ext)
    return output_format.save_new(output_path, data_array)
