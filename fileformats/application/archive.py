import typing as ty
from fileformats.core import FileSet
from fileformats.core.mixin import WithClassifier
from fileformats.generic import BinaryFile
from fileformats.core.mixin import WithMagicNumber


class Archive(BinaryFile):
    "Base class for compressed archives"
    archived_type: ty.Optional[ty.Type[FileSet]] = None


class WithArchiveClassifiers(WithClassifier):
    "Base class for compressed archives"

    classifiers_attr_name = "archived_type"
    allowed_classifiers = (FileSet,)
    generically_classifiable = True


# Compressed formats
class BaseZip(WithMagicNumber, Archive):
    ext = ".zip"
    magic_number = "504B0304"
    iana_mime = "application/zip"


class BaseBzip(WithMagicNumber, Archive):
    ext = ".bzip"
    magic_number = "425a"
    iana_mime = "application/bzip"


class BaseGzip(WithMagicNumber, Archive):
    ext = ".gz"
    magic_number = "1F8B08"
    iana_mime = "application/gzip"


class BaseTar(WithMagicNumber, Archive):
    ext = ".tar"
    magic_number = "7573746172"
    magic_number_offset = 257
    iana_mime = "application/x-tar"


class BaseTarGzip(WithMagicNumber, Archive):
    # FIXME: Should capture the relationship to Gzip and Tar somehow, but a bit
    # tricky to get it right
    ext = ".tar.gz"
    magic_number = "1F8B08"
    alternate_exts = (".tgz",)
    iana_mime = "application/x-tar+gzip"


class Zip(WithArchiveClassifiers, BaseZip):
    pass


class Bzip(WithArchiveClassifiers, BaseBzip):
    pass


class Gzip(WithArchiveClassifiers, BaseGzip):
    pass


class Tar(WithArchiveClassifiers, BaseTar):
    pass


class TarGzip(WithArchiveClassifiers, BaseTarGzip):
    pass
