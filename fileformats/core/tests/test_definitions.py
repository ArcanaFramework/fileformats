from pathlib import Path
from fileformats.core import FileSet


def test_definitions(tmp_path):
    "Check the definitions of all formats to see whether the checks can run"
    fspath = tmp_path / "test.txt"
    Path(fspath).write_text("test")
    for frmt in FileSet.all_formats:
        frmt.matches(fspath)
