import typing as ty

from docx import Document
from docx.document import Document as DocumentObject

from fileformats.core import FileSet, extra_implementation
from fileformats.vendor.openxmlformats_officedocument.application import (
    Wordprocessingml_Document as MswordX,
)


@extra_implementation(FileSet.load)
def load_docx(doc: MswordX, **kwargs: ty.Any) -> DocumentObject:
    return Document(str(doc))  # type: ignore[no-any-return]


@extra_implementation(FileSet.save)
def save_docx(doc: MswordX, data: DocumentObject, **kwargs: ty.Any) -> None:
    data.save(str(doc))
