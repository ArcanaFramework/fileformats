from pathlib import Path
import typing as ty
import tempfile
import pydra.mark
import pydra.engine.specs
from fileformats.core import hook
from fileformats.image.raster import RasterImage, Bitmap, Gif, Jpeg, Png, Tiff


@hook.converter(target_format=Bitmap, output_format=Bitmap)
@hook.converter(target_format=Gif, output_format=Gif)
@hook.converter(target_format=Jpeg, output_format=Jpeg)
@hook.converter(target_format=Png, output_format=Png)
@hook.converter(target_format=Tiff, output_format=Tiff)
@pydra.mark.task
@pydra.mark.annotate({"return": {"out_file": RasterImage}})
def convert_image(
    in_file: RasterImage,
    output_format: ty.Type[RasterImage],
    out_dir: ty.Optional[Path] = None,
):
    data_array = in_file.read_data()
    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp())
    output_path = out_dir / (in_file.fspath.stem + output_format.ext)
    return output_format.save_new(output_path, data_array)
