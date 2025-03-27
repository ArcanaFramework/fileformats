from pathlib import Path
import typing as ty
import tempfile
from pydra.compose import python
from fileformats.core import converter
from fileformats.image.raster import RasterImage, Bitmap, Gif, Jpeg, Png, Tiff


@converter(target_format=Bitmap, output_format=Bitmap)  # type: ignore[misc]
@converter(target_format=Gif, output_format=Gif)  # type: ignore[misc]
@converter(target_format=Jpeg, output_format=Jpeg)  # type: ignore[misc]
@converter(target_format=Png, output_format=Png)  # type: ignore[misc]
@converter(target_format=Tiff, output_format=Tiff)  # type: ignore[misc]
@python.define(outputs={"out_file": RasterImage})  # type: ignore[misc]
def convert_image(
    in_file: RasterImage,
    output_format: ty.Type[RasterImage],
    out_dir: ty.Optional[Path] = None,
) -> RasterImage:
    data_array = in_file.load()
    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp())
    output_path = out_dir / (
        in_file.fspath.stem + (output_format.ext if output_format.ext else "")
    )
    return output_format.new(output_path, data_array)
