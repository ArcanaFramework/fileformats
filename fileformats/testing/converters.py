import os
import typing as ty
import pydra.mark
from pathlib import Path
from fileformats.core.mark import converter
from fileformats.text import Plain as PlainText
from . import EncodedText

PathTypes = ty.Union[str, bytes, os.PathLike]


@converter(
    source_format=EncodedText, target_format=PlainText, out_filename="out_file.txt"
)
@converter(
    source_format=PlainText, target_format=EncodedText, out_filename="out_file.enc"
)
@pydra.mark.task
@pydra.mark.annotate({"return": {"out_file": Path}})
def encoder_task(
    in_file: PathTypes,
    out_filename: str,
    shift: int = 0,
) -> Path:
    with open(in_file) as f:
        contents = f.read()
    encoded = encode_text(contents, shift)
    with open(out_filename, "w") as f:
        f.write(encoded)
    return Path(out_filename).absolute()


def encode_text(text: str, shift: int) -> str:
    encoded = []
    for c in text:
        encoded.append(chr(ord(c) + shift))
    return "".join(encoded)
