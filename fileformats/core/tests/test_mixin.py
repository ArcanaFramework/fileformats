import pytest
from conftest import write_test_file
from fileformats.generic import File
from fileformats.core import mark
from fileformats.core.mixin import WithMagicNumber, WithSeparateHeader, WithSideCar
from fileformats.core.exceptions import FormatMismatchError, FileFormatsError


class FileWithMagicNumber(File, WithMagicNumber):

    ext = ".magic"
    binary = True
    magic_number = b"magicnumber"


def test_magic_number(work_dir):

    fspath = work_dir / "test.magic"
    write_test_file(
        fspath,
        FileWithMagicNumber.magic_number + b"some contents\n\n",
        binary=True,
    )
    assert FileWithMagicNumber.matches(fspath)


def test_magic_fail(work_dir):

    fspath = work_dir / "test.magic"
    write_test_file(fspath, b"NOMAGIC some contents\n\n", binary=True)
    assert not FileWithMagicNumber.matches(fspath)
    assert FileWithMagicNumber.matches(fspath, validate=False)


class Header(File):

    ext = ".hdr"

    def load(self):
        return dict(ln.split(":") for ln in self.contents.splitlines())


class FileWithSeparateHeader(WithSeparateHeader, File):

    ext = ".img"
    header_type = Header

    image_type_key = "image-type"
    image_type = "sample-image-type"

    @mark.check
    def check_image_type(self):
        if self.metadata[self.image_type_key] != self.image_type:
            raise FormatMismatchError(
                f"Mismatch in '{self.image_type_key}', expected {self.image_type}, "
                f"found {self.metadata[self.image_type_key]}"
            )


def test_with_separate_header(work_dir):

    fspath = work_dir / "image.img"
    write_test_file(fspath)
    hdr_fspath = work_dir / "image.hdr"
    hdr = {
        FileWithSeparateHeader.image_type_key: FileWithSeparateHeader.image_type,
        "dims": "10,10,20",
    }
    write_test_file(hdr_fspath, "\n".join(f"{k}:{v}" for k, v in hdr.items()))
    file = FileWithSeparateHeader(fspath)
    file.validate()
    assert file.metadata.loaded == hdr


def test_with_separate_header_fail1(work_dir):

    fspath = work_dir / "image.img"
    write_test_file(fspath)
    hdr_fspath = work_dir / "image.bad"
    hdr = {
        FileWithSeparateHeader.image_type_key: FileWithSeparateHeader.image_type,
        "dims": "10,10,20",
    }
    write_test_file(hdr_fspath, "\n".join(f"{k}:{v}" for k, v in hdr.items()))
    assert not FileWithSeparateHeader.matches([fspath, hdr_fspath])


def test_with_separate_header_fail2(work_dir):

    fspath = work_dir / "image.img"
    write_test_file(fspath)
    hdr_fspath = work_dir / "image.hdr"
    hdr = {
        FileWithSeparateHeader.image_type_key: "bad-type",
        "dims": "10,10,20",
    }
    write_test_file(hdr_fspath, "\n".join(f"{k}:{v}" for k, v in hdr.items()))
    assert not FileWithSeparateHeader.matches([fspath, hdr_fspath])


class ImageWithInlineHeader(File):

    ext = ".img"
    binary = True

    image_type_key = "image-type"
    image_type = "sample-image-type"

    header_separator = b"---END HEADER---"

    def load_metadata(self):
        hdr = self.contents.split(self.header_separator)[0].decode("utf-8")
        return dict(ln.split(":") for ln in hdr.splitlines())


class FileWithSideCar(WithSideCar, ImageWithInlineHeader):

    ext = ".img"
    primary_type = ImageWithInlineHeader
    side_car_type = Header

    experiment_type_key = "experiment-type"
    experiment_type = "sample-experiment-type"

    @mark.check
    def check_image_type(self):
        """Loaded from inline-header"""
        if self.metadata[self.image_type_key] != self.image_type:
            raise FormatMismatchError(
                f"Mismatch in '{self.image_type_key}', expected {self.image_type}, "
                f"found {self.metadata[self.image_type_key]}"
            )

    @mark.check
    def check_experiment_type(self):
        """Loaded from side-car"""
        if self.metadata[self.experiment_type_key] != self.experiment_type:
            raise FormatMismatchError(
                f"Mismatch in '{self.experiment_type_key}', expected {self.experiment_type}, "
                f"found {self.metadata[self.experiment_type_key]}"
            )


def test_with_side_car(work_dir):

    fspath = work_dir / "image.img"
    hdr = {
        ImageWithInlineHeader.image_type_key: ImageWithInlineHeader.image_type,
    }
    write_test_file(
        fspath,
        (
            "\n".join(f"{k}:{v}" for k, v in hdr.items()).encode("utf-8")
            + ImageWithInlineHeader.header_separator
            + b"SOMERANDOMBYTESDATA"
        ),
        binary=True,
    )
    side_car_fs_path = work_dir / "image.hdr"
    side_car = {
        FileWithSideCar.experiment_type_key: FileWithSideCar.experiment_type,
    }
    write_test_file(
        side_car_fs_path, "\n".join(f"{k}:{v}" for k, v in side_car.items())
    )
    assert FileWithSideCar.matches([fspath, side_car_fs_path])


def test_with_side_car_fail1(work_dir):

    fspath = work_dir / "image.img"
    hdr = {
        ImageWithInlineHeader.image_type_key: ImageWithInlineHeader.image_type,
    }
    write_test_file(
        fspath,
        (
            "\n".join(f"{k}:{v}" for k, v in hdr.items()).encode("utf-8")
            + b"BAD SEPARATOR"  # NB: bad separator
            + b"SOMERANDOMBYTESDATA"
        ),
        binary=True,
    )
    side_car_fs_path = work_dir / "image.hdr"
    side_car = {
        FileWithSideCar.experiment_type_key: FileWithSideCar.experiment_type,
    }
    write_test_file(
        side_car_fs_path, "\n".join(f"{k}:{v}" for k, v in side_car.items())
    )
    assert not FileWithSideCar.matches([fspath, side_car_fs_path])


def test_with_side_car_fail2(work_dir):

    fspath = work_dir / "image.img"
    hdr = {
        ImageWithInlineHeader.image_type_key: "bad-image-type",  # NB: bad type
    }
    write_test_file(
        fspath,
        (
            "\n".join(f"{k}:{v}" for k, v in hdr.items()).encode("utf-8")
            + ImageWithInlineHeader.header_separator
            + b"SOMERANDOMBYTESDATA"
        ),
        binary=True,
    )
    side_car_fs_path = work_dir / "image.hdr"
    side_car = {
        FileWithSideCar.experiment_type_key: FileWithSideCar.experiment_type,
    }
    write_test_file(
        side_car_fs_path, "\n".join(f"{k}:{v}" for k, v in side_car.items())
    )
    assert not FileWithSideCar.matches([fspath, side_car_fs_path])


def test_with_side_car_fail3(work_dir):

    fspath = work_dir / "image.img"
    hdr = {
        ImageWithInlineHeader.image_type_key: ImageWithInlineHeader.image_type,
    }
    write_test_file(
        fspath,
        (
            "\n".join(f"{k}:{v}" for k, v in hdr.items()).encode("utf-8")
            + ImageWithInlineHeader.header_separator
            + b"SOMERANDOMBYTESDATA"
        ),
        binary=True,
    )
    side_car_fs_path = work_dir / "image.hdr"
    side_car = {
        FileWithSideCar.experiment_type_key: "bad-experiment-type",  # NB: bad type
    }
    write_test_file(
        side_car_fs_path, "\n".join(f"{k}:{v}" for k, v in side_car.items())
    )
    assert not FileWithSideCar.matches([fspath, side_car_fs_path])


def test_with_side_car_fail_overlap(work_dir):

    fspath = work_dir / "image.img"
    hdr = {
        ImageWithInlineHeader.image_type_key: ImageWithInlineHeader.image_type,
        "dims": "10,20,30",  # NB: overlaps with header
    }
    write_test_file(
        fspath,
        (
            "\n".join(f"{k}:{v}" for k, v in hdr.items()).encode("utf-8")
            + ImageWithInlineHeader.header_separator
            + b"SOMERANDOMBYTESDATA"
        ),
        binary=True,
    )
    side_car_fs_path = work_dir / "image.hdr"
    side_car = {
        FileWithSideCar.experiment_type_key: FileWithSideCar.experiment_type,
        "dims": "10,20,30",  # NB: overlaps with header
    }
    write_test_file(
        side_car_fs_path, "\n".join(f"{k}:{v}" for k, v in side_car.items())
    )
    with pytest.raises(FileFormatsError):
        assert FileWithSideCar.matches([fspath, side_car_fs_path])
