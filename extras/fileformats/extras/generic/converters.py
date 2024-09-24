import tempfile
from pathlib import Path
import typing as ty
import pydra.mark
from fileformats.core import converter, FileSet
from fileformats.generic import DirectoryOf, SetOf, TypedDirectory, TypedSet

T = FileSet.type_var("T")


@converter(target_format=SetOf[T], source_format=DirectoryOf[T])  # type: ignore[misc]
@pydra.mark.task  # type: ignore[misc]
@pydra.mark.annotate({"return": {"out_file": TypedSet}})  # type: ignore[misc]
def list_dir_contents(in_file: TypedDirectory) -> TypedSet:
    classified_set: ty.Type[TypedSet] = SetOf.__class_getitem__(*in_file.content_types)  # type: ignore[assignment, arg-type]
    return classified_set(in_file.contents)


@converter(target_format=DirectoryOf[T], source_format=SetOf[T])  # type: ignore[misc]
@pydra.mark.annotate({"return": {"out_file": TypedDirectory}})  # type: ignore[misc]
@pydra.mark.task  # type: ignore[misc]
def put_contents_in_dir(
    in_file: TypedSet,
    out_dir: ty.Optional[Path] = None,
    copy_mode: FileSet.CopyMode = FileSet.CopyMode.copy,
) -> TypedDirectory:
    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp())
    for fset in in_file.contents:
        fset.copy(out_dir, mode=copy_mode)
    classified_dir: ty.Type[TypedDirectory] = DirectoryOf.__class_getitem__(  # type: ignore[assignment]
        *in_file.content_types  # type: ignore[arg-type]
    )
    return classified_dir(out_dir)
