from fileformats.core.base import FileSet
from fileformats.core import mark


class Foo(FileSet):
    @mark.required(in_=("type1", "type2"))
    @property
    def filetype(self):
        return self.metadata["filetype"]


# def test_copy_to(work_dir):
