import os.path
import sys
import tempfile
import tarfile
import zipfile
from pathlib import Path
import attrs
import pydra.mark
from pydra.engine.specs import MultiOutputObj, File, Directory
from fileformats.core.base import FileSet
from fileformats.core.utils import set_cwd
from fileformats.core import mark
from fileformats.archive import Zip, Tar, Tar_Gzip


TAR_COMPRESSION_TYPES = ["", "gz", "bz2", "xz"]


@mark.converter(source_format=FileSet, target_format=Tar_Gzip, compression="gz")
@mark.converter(source_format=FileSet, target_format=Tar)
@pydra.mark.task
@pydra.mark.annotate(
    {
        "in_file": FileSet,
        "out_file": Tar,
        "filter": str,
        "compression": (
            str,
            {
                "help_string": (
                    "The type of compression applied to tar file, "
                    "', '".join(TAR_COMPRESSION_TYPES)
                ),
                "allowed_values": list(TAR_COMPRESSION_TYPES),
            },
        ),
        "format": int,
        "ignore_zeros": bool,
        "return": {"out_file": Tar},
    }
)
def create_tar(
    in_file,
    out_file=None,
    base_dir=".",
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
        out_file = in_file[0] + ext

    out_file = os.path.abspath(out_file)

    with tarfile.open(
        out_file,
        mode=f"w:{compression}",
        format=format,
        ignore_zeros=ignore_zeros,
        encoding=encoding,
    ) as tfile, set_cwd(base_dir):
        for path in in_file:
            tfile.add(relative_path(path, base_dir), filter=filter)

    return out_file


@mark.converter(source_format=Tar, target_format=FileSet)
@mark.converter(source_format=Tar_Gzip, target_format=FileSet)
@pydra.mark.task
@pydra.mark.annotate({"return": {"out_file": MultiOutputObj}})
def extract_tar(
    in_file: File,
    extract_dir: Directory,
    bufsize: int = 10240,
    compression_type: str = "*",
):

    if extract_dir == attrs.NOTHING:
        extract_dir = tempfile.mkdtemp()
    else:
        extract_dir = os.path.abspath(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)

    if not compression_type:
        compression_type = ""

    with tarfile.open(in_file, mode=f"r:{compression_type}") as tfile:
        tfile.extractall(path=extract_dir)

    return [os.path.join(extract_dir, f) for f in os.listdir(extract_dir)]


@mark.converter(
    source_format=FileSet, target_format=Zip, compression=zipfile.ZIP_DEFLATED
)
@pydra.mark.task
@pydra.mark.annotate(
    {
        "in_file": File,
        "out_file": str,
        "compression": (
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
        ),
        "allowZip64": bool,
        "return": {"out_file": Zip},
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

    if out_file == attrs.NOTHING:
        out_file = Path(in_file[0]).name + ".zip"

    if base_dir == attrs.NOTHING:
        base_dir = Path(in_file[0]).parent

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
        for path in in_file:
            path = Path(path)
            if path.is_dir():
                for dpath, _, files in os.walk(path):
                    zfile.write(relative_path(dpath, base_dir))
                    for fname in files:
                        fpath = os.path.join(dpath, fname)
                        zfile.write(relative_path(fpath, base_dir))
            else:
                zfile.write(relative_path(path, base_dir))
    return out_file


@mark.converter(
    source_format=Zip, target_format=FileSet, compression=zipfile.ZIP_DEFLATED
)
@pydra.mark.task
@pydra.mark.annotate({"return": {"out_file": MultiOutputObj}})
def extract_zip(in_file: File, extract_dir: Directory):

    if extract_dir == attrs.NOTHING:
        extract_dir = tempfile.mkdtemp()
    else:
        extract_dir = os.path.abspath(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(in_file) as zfile:
        zfile.extractall(path=extract_dir)

    return [os.path.join(extract_dir, f) for f in os.listdir(extract_dir)]


def relative_path(path, base_dir):
    path = os.path.abspath(path)
    relpath = os.path.relpath(path, base_dir)
    if ".." in relpath:
        raise RuntimeError(
            f"Cannot add {path} to archive as it is not a "
            f"subdirectory of {base_dir}"
        )
    return relpath
