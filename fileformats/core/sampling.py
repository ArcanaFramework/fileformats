from pathlib import Path
import random
import string
from functools import cached_property
import typing as ty
import fileformats.core


class SampleFileGenerator:
    """Generates sample files. Designed to be used within generate_sample_data overrides

    Parameters
    ----------
    dest_dir : Path
        the directory to write the sample files to
    seed : int
        the seed for the random number generator
    fname_stem : str
        the stem of the file name to generate
    """

    dest_dir: Path
    seed: int
    fname_stem: str

    FNAME_STEM_LENGTH = 24

    def __init__(self, dest_dir: Path, seed: int, fname_stem: str = None):
        self.dest_dir = dest_dir
        self.seed = seed
        self.fname_stem = (
            self._generate_fname_stem() if fname_stem is None else fname_stem
        )

    def _generate_fname_stem(self):
        return "".join(
            self.rng.choices(
                string.ascii_letters + string.digits, k=self.FNAME_STEM_LENGTH
            )
        )

    @cached_property
    def rng(self):
        return random.Random(self.seed)

    def generate(
        self,
        file_type: ty.Type["fileformats.core.FileSet"],
        contents: ty.Union[str, bytes] = None,
        fill: int = 0,
        **kwargs,
    ):
        """Generates a random file of length `length` and extension `ext`

        Parameters
        ----------
        file_type : Type[FileSet]
            type of the file to generate the filename for, used to append any extensions
            and seed the random number generator if required
        contents : Union[str, bytes]
            the contents of the file to write
        fill : int
            length of the random string to generate for the file contents. Will be appended
            after any explicitly provided contents
        **kwargs : dict
            additional keyword arguments to pass to generate_fspath

        Returns
        -------
        fspath : Path
            path to the randomly generated file
        """
        if not contents and not fill:
            raise ValueError("Either contents or random_fill_length must be provided")
        fspath = self.generate_fspath(file_type, **kwargs)
        fspath.parent.mkdir(parents=True, exist_ok=True)
        try:
            is_binary = file_type.binary
        except AttributeError:
            is_binary = False
        if not contents:
            contents = (
                bytes(random.choices(list(range(256)), k=fill))
                if is_binary
                else "".join(random.choices(string.printable, k=fill))
            )
        else:
            contents_type = bytes if is_binary else str
            if not isinstance(contents, bytes):
                raise TypeError(
                    f"contents must be {contents_type} for {file_type} files, "
                    f"not {type(contents)}"
                )
        if is_binary:
            fspath.write_bytes(contents)
        else:
            fspath.write_text(contents)
        return fspath

    def generate_fspath(
        self,
        file_type: ty.Optional[ty.Type["fileformats.core.FileSet"]] = None,
        fname_stem: ty.Optional[str] = None,
        relpath: ty.Optional[Path] = None,
    ):
        """Generates a random file path in the destination directory of length `length`
        and extension `ext`

        Parameters
        ----------
        file_type : Type[FileSet]
            type of the file to generate the filename for, used to append any extensions
            and seed the random number generator if required
        fname_stem : str, optional or bool
            Use explicitly provided if it is a string
        relpath : Path
            the path to generate the filename at, relative to the destination directory

        Returns
        -------
        fspath : Path
            randomly generated file-system path
        """
        if file_type is None:
            import fileformats.generic

            file_type = fileformats.generic.FsObject
        if fname_stem is not None:
            fname = fname_stem
        else:
            fname = self.fname_stem
        if file_type and file_type.ext:
            fname += file_type.ext
        fspath = self.dest_dir
        if relpath:
            fspath /= relpath
        return fspath / fname

    def child(
        self, dest_dir: ty.Optional[Path] = None, fname_stem: str = None
    ) -> "SampleFileGenerator":
        """Creates a new instance of SampleFileGenerator with the same destination
        directory and seed, but a new random filename stem

        Parameters
        ----------
        relpath : Path, optional
            the path to generate the filename at, relative to the destination directory
        fname_stem : str, optional
            the stem of the file name to generate

        Returns
        -------
        SampleFileGenerator
            the new instance of SampleFileGenerator
        """
        if dest_dir is None:
            dest_dir = self.dest_dir
        kwargs = {"fname_stem": fname_stem} if fname_stem else {}
        return SampleFileGenerator(
            dest_dir, seed=self.rng.randint(0, 2**32 - 1), **kwargs
        )
