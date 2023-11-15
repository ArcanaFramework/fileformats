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
from fileformats.core import hook, FileSet
from fileformats.application import Zip, Tar, TarGzip


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


@hook.converter(source_format=FsObject, target_format=Tar)
@hook.converter(source_format=FsObject, target_format=TarGzip, compression="gz")
@hook.converter(source_format=Compressed, target_format=Tar[Compressed])
@hook.converter(
    source_format=Compressed, target_format=TarGzip[Compressed], compression="gz"
)
@pydra.mark.task
@pydra.mark.annotate(
    {
        "return": {"out_file": Path},
    }
)
def create_tar(
    in_file: FsObject,
    out_file: ty.Optional[Path] = None,
    base_dir: ty.Optional[Path] = None,
    filter: ty.Optional[ty.Callable] = None,
    compression: ty.Optional[str] = None,
    format: int = tarfile.DEFAULT_FORMAT,
    ignore_zeros: bool = False,
    encoding: str = tarfile.ENCODING,
) -> Path:

    if len(in_file.fspaths) > 1:
        raise NotImplementedError(
            "Can only archive file-sets with single paths currently"
        )

    if not compression:
        compression = ""
        ext = ".tar"
    else:
        ext = ".tar." + compression

    if not out_file:
        out_file = Path(Path(in_file).name + ext)

    if base_dir is None:
        base_dir = Path(in_file).parent

    out_file = out_file.absolute()

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


@hook.converter(source_format=Tar, target_format=FsObject)
@hook.converter(source_format=TarGzip, target_format=FsObject)
@hook.converter(source_format=Tar[Compressed], target_format=Compressed)
@hook.converter(source_format=TarGzip[Compressed], target_format=Compressed)
@pydra.mark.task
@pydra.mark.annotate({"return": {"out_file": Path}})
def extract_tar(
    in_file: FsObject,
    extract_dir: Path,
    bufsize: int = 10240,
    compression_type: str = "*",
) -> Path:

    if extract_dir == attrs.NOTHING:
        extract_dir = Path(tempfile.mkdtemp())
    else:
        extract_dir = extract_dir.absolute()
        os.makedirs(extract_dir, exist_ok=True)
    extract_dir = Path(extract_dir)

    if not compression_type:
        compression_type = ""

    with tarfile.open(in_file, mode=f"r:{compression_type}") as tfile:
        tfile.extractall(path=extract_dir)

    extracted = [extract_dir / f for f in os.listdir(extract_dir)]
    if len(extracted) > 1:
        raise NotImplementedError(
            "Can't handle zip files with more than one path currently"
        )
    return extracted[0]


@hook.converter(source_format=FsObject, target_format=Zip)
@hook.converter(source_format=Compressed, target_format=Zip[Compressed])
@pydra.mark.task
@pydra.mark.annotate(
    {
        "return": {"out_file": Zip},
    }
)
def create_zip(
    in_file: FsObject,
    out_file: Path,
    base_dir: Path,
    compression: int = zipfile.ZIP_DEFLATED,
    allowZip64: bool = True,
    compresslevel: ty.Optional[int] = None,
    strict_timestamps: bool = True,
) -> Zip:

    if len(in_file.fspaths) > 1:
        raise NotImplementedError(
            "Can only archive file-sets with single paths currently"
        )

    if out_file == attrs.NOTHING:
        out_file = Path(Path(in_file).name + ".zip")

    if base_dir == attrs.NOTHING:
        base_dir = Path(in_file).parent

    out_file = out_file.absolute()

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


@hook.converter(source_format=Zip, target_format=FsObject)
@hook.converter(source_format=Zip[Compressed], target_format=Compressed)
@pydra.mark.task
@pydra.mark.annotate({"return": {"out_file": Path}})
def extract_zip(in_file: Zip, extract_dir: Path) -> Path:

    if extract_dir == attrs.NOTHING:
        extract_dir = Path(tempfile.mkdtemp())
    else:
        extract_dir = extract_dir.absolute()
        os.makedirs(extract_dir, exist_ok=True)
    extract_dir = Path(extract_dir)

    with zipfile.ZipFile(in_file) as zfile:
        zfile.extractall(path=extract_dir)

    extracted = [extract_dir / f for f in os.listdir(extract_dir)]
    if len(extracted) > 1:
        raise NotImplementedError(
            "Can't handle zip files with more than one path currently"
        )
    return extracted[0]


def relative_path(path, base_dir):
    path = os.path.abspath(path)
    relpath = os.path.relpath(path, base_dir)
    if ".." in relpath:
        raise RuntimeError(
            f"Cannot add {path} to archive as it is not a "
            f"subdirectory of {base_dir}"
        )
    return relpath
