import os
import typing as ty
import itertools
from pathlib import Path
from fileformats.core import FileSet, extra_implementation
from fileformats.core import SampleFileGenerator
from .fsobject import FsObject
from .file import File
from .set import SetOf
from .directory import Directory, DirectoryOf


# Methods to generate sample files, typically used in testing
FILE_FILL_LENGTH = 256


@extra_implementation(FileSet.generate_sample_data)
def fsobject_generate_sample_data(
    fsobject: FsObject,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return [generator.generate(File, fill=FILE_FILL_LENGTH)]


@extra_implementation(FileSet.generate_sample_data)
def file_generate_sample_data(
    file: File,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    contents = None
    if getattr(file, "binary", False):
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


@extra_implementation(FileSet.generate_sample_data)
def directory_generate_sample_data(
    directory: Directory,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    a_dir = generator.generate_fspath(Directory)
    a_dir.mkdir()
    File.sample_data(
        generator.child(dest_dir=a_dir)
    )  # Add a sample file for good measure
    return [a_dir]


@extra_implementation(FileSet.generate_sample_data)
def directory_containing_generate_sample_data(
    directory: DirectoryOf,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    a_dir = generator.generate_fspath(Directory)
    a_dir.mkdir()
    for tp in directory.content_types:
        tp.sample_data(generator.child(dest_dir=a_dir))
    return [a_dir]


@extra_implementation(FileSet.generate_sample_data)
def set_of_sample_data(
    set_of: SetOf,
    generator: SampleFileGenerator,
) -> ty.List[Path]:
    return list(
        itertools.chain(
            *(tp.sample_data(generator.child()) for tp in set_of.content_types)
        )
    )
