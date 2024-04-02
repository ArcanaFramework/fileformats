import os
import typing as ty
import itertools
from pathlib import Path
from fileformats.core.fileset import FileSet
from fileformats.core import SampleFileGenerator
from .fsobject import FsObject
from .file import File
from .set import SetOf
from .directory import Directory, DirectoryContaining


# Methods to generate sample files, typically used in testing
FILE_FILL_LENGTH = 256


@FileSet.generate_sample_data.register
def fsobject_generate_sample_data(
    fsobject: FsObject,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return [generator.generate(File, fill=FILE_FILL_LENGTH)]


@FileSet.generate_sample_data.register
def file_generate_sample_data(
    file: File,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    contents = None
    if file.binary:
        if hasattr(file, "magic_number"):
            offset = getattr(file, "magic_number_offset", 0)
            contents = os.urandom(offset)
            magic_number = getattr(file, "magic_number", b"")
            if isinstance(magic_number, str):
                magic_number = bytes.fromhex(magic_number)
            contents += magic_number
        elif hasattr(file, "magic_pattern"):
            raise NotImplementedError(
                "Sampling of magic version file types is not implemented yet"
            )
    fspaths = [generator.generate(file, contents=contents, fill=FILE_FILL_LENGTH)]
    if hasattr(file, "header_type"):
        fspaths.extend(file.header_type.sample_data(generator))
    if hasattr(file, "side_car_types"):
        for side_car_type in file.side_car_types:
            fspaths.extend(side_car_type.sample_data(generator))
    return fspaths


@FileSet.generate_sample_data.register
def directory_generate_sample_data(
    directory: Directory,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    a_dir = generator.generate_fspath(Directory)
    a_dir.mkdir()
    File.sample_data(
        generator.child(dest_dir=a_dir)
    )  # Add a sample file for good measure
    return [a_dir]


@FileSet.generate_sample_data.register
def directory_containing_generate_sample_data(
    directory: DirectoryContaining,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    a_dir = generator.generate_fspath(Directory)
    a_dir.mkdir()
    for tp in directory.content_types:
        tp.sample_data(generator.child(dest_dir=a_dir))
    return [a_dir]


@FileSet.generate_sample_data.register
def set_of_sample_data(
    set_of: SetOf,
    generator: SampleFileGenerator,
) -> ty.Iterable[Path]:
    return list(
        itertools.chain(
            *(tp.sample_data(generator.child()) for tp in set_of.content_types)
        )
    )
