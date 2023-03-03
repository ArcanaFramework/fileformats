import os.path
import sys
import typing as ty
import tempfile
import tarfile
import zipfile
from pathlib import Path
import attrs
import pydra.mark
import pydra.engine.specs
from fileformats.generic import FsObject
from fileformats.core.utils import set_cwd
from fileformats.core import mark, FileSet
from fileformats.archive import Zip, Tar, TarGzip


TAR_COMPRESSION_TYPES = ["", "gz", "bz2", "xz"]

TAR_COMPRESSION_ANNOT = (
    str,
    {
        "help_string": (
            "The type of compression applied to tar file, "
            "', '".join(TAR_COMPRESSION_TYPES)
        ),
        "allowed_values": list(TAR_COMPRESSION_TYPES),
    },
)

ZIP_COMPRESSION_ANNOT = (
    int,
    {
        "help_string": (
            "The type of compression applied to zip file, "
            "see https://docs.python.org/3/library/zipfile.html#zipfile.ZIP_DEFLATED "
            "for valid compression types"
        ),
        "allowed_values": [
            zipfile.ZIP_STORED,
            zipfile.ZIP_DEFLATED,
            zipfile.ZIP_BZIP2,
            zipfile.ZIP_LZMA,
        ],
    },
)

Compressed = FileSet.type_var("Compressed")

PathLike = ty.Union[str, bytes, os.PathLike]


@mark.converter(source_format=FsObject, target_format=Tar)
@mark.converter(source_format=FsObject, target_format=TarGzip, compression="gz")
@mark.converter(source_format=Compressed, target_format=Tar[Compressed])
@mark.converter(
    source_format=Compressed, target_format=TarGzip[Compressed], compression="gz"
)
@pydra.mark.task
@pydra.mark.annotate(
    {
        "in_file": PathLike,
        "out_file": str,
        "filter": str,
        "compression": str,  # TAR_COMPRESSION_ANNOT,
        "format": int,
        "ignore_zeros": bool,
        "return": {"out_file": Path},
    }
)
def create_tar(
    in_file,
    out_file=None,
    base_dir=None,
    filter=None,
    compression=None,
    format=tarfile.DEFAULT_FORMAT,
    ignore_zeros=False,
    encoding=tarfile.ENCODING,
):
    return _create_tar(
        in_file=in_file,
        out_file=out_file,
        base_dir=base_dir,
        filter=filter,
        compression=compression,
        format=format,
        ignore_zeros=ignore_zeros,
        encoding=encoding,
    )


# @mark.converter(source_format=Directory, target_format=Tar_Gzip, compression="gz")
# @mark.converter(source_format=Directory, target_format=Tar)
# @pydra.mark.task
# @pydra.mark.annotate(
#     {
#         "in_file": pydra.engine.specs.Directory,
#         "out_file": str,
#         "filter": str,
#         "compression": str,  # TAR_COMPRESSION_ANNOT,
#         "format": int,
#         "ignore_zeros": bool,
#         "return": {"out_file": Path},
#     }
# )
# def tar_dir(
#     in_file,
#     out_file=None,
#     base_dir=None,
#     filter=None,
#     compression=None,
#     format=tarfile.DEFAULT_FORMAT,
#     ignore_zeros=False,
#     encoding=tarfile.ENCODING,
# ):
#     return _create_tar(
#         in_file=in_file,
#         out_file=out_file,
#         base_dir=base_dir,
#         filter=filter,
#         compression=compression,
#         format=format,
#         ignore_zeros=ignore_zeros,
#         encoding=encoding,
#     )


def _create_tar(
    in_file,
    out_file=None,
    base_dir=None,
    filter=None,
    compression=None,
    format=tarfile.DEFAULT_FORMAT,
    ignore_zeros=False,
    encoding=tarfile.ENCODING,
):

    if not compression:
        compression = ""
        ext = ".tar"
    else:
        ext = ".tar." + compression

    if not out_file:
        out_file = Path(in_file).name + ext

    if base_dir is None:
        base_dir = Path(in_file).parent

    out_file = os.path.abspath(out_file)

    with tarfile.open(
        out_file,
        mode=f"w:{compression}",
        format=format,
        ignore_zeros=ignore_zeros,
        encoding=encoding,
    ) as tfile, set_cwd(base_dir):
        for fspath in in_file.fspaths:
            tfile.add(relative_path(fspath, base_dir), filter=filter)

    return Path(out_file)


@mark.converter(source_format=Tar, target_format=FsObject)
@mark.converter(source_format=TarGzip, target_format=FsObject)
@mark.converter(source_format=Tar[Compressed], target_format=Compressed)
@mark.converter(source_format=TarGzip[Compressed], target_format=Compressed)
@pydra.mark.task
@pydra.mark.annotate({"return": {"out_file": pydra.engine.specs.MultiOutputObj}})
def extract_tar(
    in_file: PathLike,
    extract_dir: PathLike,
    bufsize: int = 10240,
    compression_type: str = "*",
) -> ty.Iterable[Path]:

    if extract_dir == attrs.NOTHING:
        extract_dir = tempfile.mkdtemp()
    else:
        extract_dir = os.path.abspath(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)
    extract_dir = Path(extract_dir)

    if not compression_type:
        compression_type = ""

    with tarfile.open(in_file, mode=f"r:{compression_type}") as tfile:
        tfile.extractall(path=extract_dir)

    return [extract_dir / f for f in os.listdir(extract_dir)]


@mark.converter(source_format=FsObject, target_format=Zip)
@mark.converter(source_format=Compressed, target_format=Zip[Compressed])
@pydra.mark.task
@pydra.mark.annotate(
    {
        "in_file": PathLike,
        "out_file": str,
        "compression": int,  # ZIP_COMPRESSION_ANNOT,
        "allowZip64": bool,
        "return": {"out_file": PathLike},
    }
)
def create_zip(
    in_file,
    out_file,
    base_dir,
    compression=zipfile.ZIP_DEFLATED,
    allowZip64=True,
    compresslevel=None,
    strict_timestamps=True,
):
    return _create_zip(
        in_file=in_file,
        out_file=out_file,
        base_dir=base_dir,
        compression=compression,
        allowZip64=allowZip64,
        compresslevel=compresslevel,
        strict_timestamps=strict_timestamps,
    )


# @mark.converter(source_format=Directory, target_format=Zip)
# @pydra.mark.task
# @pydra.mark.annotate(
#     {
#         "in_file": pydra.engine.specs.Directory,
#         "out_file": str,
#         "compression": int,  # ZIP_COMPRESSION_ANNOT,
#         "allowZip64": bool,
#         "return": {"out_file": Path},
#     }
# )
# def zip_dir(
#     in_file,
#     out_file,
#     base_dir,
#     compression=zipfile.ZIP_DEFLATED,
#     allowZip64=True,
#     compresslevel=None,
#     strict_timestamps=True,
# ):
#     return _create_zip(
#         in_file=in_file,
#         out_file=out_file,
#         base_dir=base_dir,
#         compression=compression,
#         allowZip64=allowZip64,
#         compresslevel=compresslevel,
#         strict_timestamps=strict_timestamps,
#     )


def _create_zip(
    in_file,
    out_file,
    base_dir,
    compression=zipfile.ZIP_DEFLATED,
    allowZip64=True,
    compresslevel=None,
    strict_timestamps=True,
):

    if out_file == attrs.NOTHING:
        out_file = Path(in_file).name + ".zip"

    if base_dir == attrs.NOTHING:
        base_dir = Path(in_file).parent

    out_file = os.path.abspath(out_file)

    zip_kwargs = {}
    if not strict_timestamps:  # Truthy is the default in earlier versions
        if sys.version_info.major <= 3 and sys.version_info.minor < 8:
            raise Exception(
                "Must be using Python >= 3.8 to pass "
                f"strict_timestamps={strict_timestamps!r}"
            )

        zip_kwargs["strict_timestamps"] = strict_timestamps

    with zipfile.ZipFile(
        out_file,
        mode="w",
        compression=compression,
        allowZip64=allowZip64,
        compresslevel=compresslevel,
        **zip_kwargs,
    ) as zfile, set_cwd(base_dir):
        for fspath in in_file.fspaths:
            fspath = Path(fspath)
            if fspath.is_dir():
                for dpath, _, files in os.walk(fspath):
                    zfile.write(relative_path(dpath, base_dir))
                    for fname in files:
                        fpath = os.path.join(dpath, fname)
                        zfile.write(relative_path(fpath, base_dir))
            else:
                zfile.write(relative_path(fspath, base_dir))
    return Path(out_file)


@mark.converter(source_format=Zip, target_format=FsObject)
@mark.converter(source_format=Zip[Compressed], target_format=Compressed)
@pydra.mark.task
@pydra.mark.annotate({"return": {"out_file": pydra.engine.specs.MultiOutputObj}})
def extract_zip(in_file: PathLike, extract_dir: PathLike):

    if extract_dir == attrs.NOTHING:
        extract_dir = tempfile.mkdtemp()
    else:
        extract_dir = os.path.abspath(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)
    extract_dir = Path(extract_dir)

    with zipfile.ZipFile(in_file) as zfile:
        zfile.extractall(path=extract_dir)

    return [extract_dir / f for f in os.listdir(extract_dir)]


def relative_path(path, base_dir):
    path = os.path.abspath(path)
    relpath = os.path.relpath(path, base_dir)
    if ".." in relpath:
        raise RuntimeError(
            f"Cannot add {path} to archive as it is not a "
            f"subdirectory of {base_dir}"
        )
    return relpath
