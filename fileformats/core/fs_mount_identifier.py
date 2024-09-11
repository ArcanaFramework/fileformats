import os
import typing as ty
import string
from pathlib import Path
import platform
import time
import re
from contextlib import contextmanager
import subprocess as sp
from .utils import logger

PathLike = ty.Union[str, Path]


class FsMountIdentifier:
    """Used to check the mount type that given file paths reside on in order to determine
    features that can be used (e.g. symlinks)"""

    @classmethod
    def symlinks_supported(cls, path: PathLike) -> bool:
        """
        Check whether a file path is on a CIFS filesystem mounted in a POSIX host.

        POSIX hosts are assumed to have the ``mount`` command.

        On Windows, Docker mounts host directories into containers through CIFS
        shares, which has support for Minshall+French symlinks, or text files that
        the CIFS driver exposes to the OS as symlinks.
        We have found that under concurrent access to the filesystem, this feature
        can result in failures to create or read recently-created symlinks,
        leading to inconsistent behavior and ``FileNotFoundError`` errors.

        This check is written to support disabling symlinks on CIFS shares.

        NB: This function and sub-functions are modified from the nipype.utils.filemanip module


        NB: Adapted from https://github.com/nipy/nipype
        """
        return cls.get_mount(path)[1] != "cifs"

    @classmethod
    def on_same_mount(cls, path1: PathLike, path2: PathLike) -> bool:
        """Checks whether two or paths are on the same logical file system"""
        return cls.get_mount(path1)[0] == cls.get_mount(path2)[0]

    @classmethod
    def get_mount(cls, path: PathLike) -> ty.Tuple[Path, str]:
        """Get the mount point for a given file-system path

        Parameters
        ----------
        path: os.PathLike
            the file-system path to identify the mount of

        Returns
        -------
        mount_point: os.PathLike
            the root of the mount the path sits on
        fstype : str
            the type of the file-system (e.g. ext4 or cifs)"""
        strpath = str(Path(path).absolute())
        mount_table = cls.get_mount_table()
        matches = sorted(
            ((Path(p), t) for p, t in mount_table if strpath.startswith(p)),
            key=lambda m: len(str(m[0])),
        )
        if not matches:
            raise ValueError(
                f"Path {strpath} is not on a known mount point:\n{mount_table}"
            )
        # return mount point with longest matching prefix
        return matches[-1]

    @classmethod
    def generate_mount_table(cls) -> ty.List[ty.Tuple[str, str]]:
        """
        Construct a reverse-length-ordered list of mount points that fall under a CIFS mount.

        This precomputation allows efficient checking for whether a given path
        would be on a CIFS filesystem.
        On systems without a ``mount`` command, or with no CIFS mounts, returns an
        empty list.

        """
        if platform.system() == "Windows":
            drive_names = [
                c + ":" for c in string.ascii_uppercase if os.path.exists(c + ":")
            ]
            drives = []
            for drive_name in drive_names:
                result = sp.run(
                    ["fsutil", "fsinfo", "fstype", drive_name],
                    capture_output=True,
                    text=True,
                )
                fstype = result.stdout.strip().split(" ")[-1].lower()
                drives.append((drive_name, fstype))
            return drives
        exit_code, output = sp.getstatusoutput("mount")
        if exit_code != 0:
            raise RuntimeError(
                "Failed to get mount table (exit code {}): {}".format(exit_code, output)
            )
        return cls.parse_mount_table(exit_code, output)

    @classmethod
    def parse_mount_table(
        cls, exit_code: int, output: str
    ) -> ty.List[ty.Tuple[str, str]]:
        """
        Parse the output of ``mount`` to produce (path, fs_type) pairs.

        Separated from _generate_cifs_table to enable testing logic with real
        outputs

        """
        # Linux mount example:  sysfs on /sys type sysfs (rw,nosuid,nodev,noexec)
        #                          <PATH>^^^^      ^^^^^<FSTYPE>
        # OSX mount example:    /dev/disk2 on / (hfs, local, journaled)
        #                               <PATH>^  ^^^<FSTYPE>
        pattern = re.compile(r".*? on (/.*?) (?:type |\()([^\s,\)]+)")

        # Keep line and match for error reporting (match == None on failure)
        # Ignore empty lines
        matches = [(ll, pattern.match(ll)) for ll in output.strip().splitlines() if ll]

        # (path, fstype) tuples, sorted by path length (longest first)
        mounts: ty.List[ty.Tuple[str, str]] = sorted(
            (match.groups() for _, match in matches if match is not None),  # type: ignore
            key=lambda x: len(x[0]),
            reverse=True,
        )

        # Report failures as warnings
        for line, match in matches:
            if match is None:
                logger.debug("Cannot parse mount line: '%s'", line)

        return mounts

    @classmethod
    def get_mount_table(cls) -> ty.List[ty.Tuple[str, str]]:
        if cls._mount_table is None:
            cls._mount_table = cls.generate_mount_table()
        return cls._mount_table

    @classmethod
    @contextmanager
    def patch_table(cls, mount_table: ty.List[ty.Tuple[str, str]]) -> ty.Iterator[None]:
        """Patch the mount table with new values. Used in test routines"""
        orig_table = cls._mount_table
        cls._mount_table = list(mount_table)
        try:
            yield
        finally:
            cls._mount_table = orig_table

    @classmethod
    def get_mtime_resolution(cls, path: PathLike) -> int:
        """Get the mount point for a given file-system path

        Parameters
        ----------
        path: os.PathLike
            the file-system path to identify the mount of

        Returns
        -------
        mount_point: os.PathLike
            the root of the mount the path sits on
        fstype : str
            the type of the file-system (e.g. ext4 or cifs)"""
        mount_point, fstype = cls.get_mount(path)
        try:
            resolution = cls.FS_MTIME_NS_RESOLUTION[fstype]
        except KeyError:
            try:
                resolution = cls.measure_mtime_resolution(mount_point)
            except (RuntimeError, OSError):
                # Fallback to the largest known mtime
                resolution = max(cls.FS_MTIME_NS_RESOLUTION.values())
        return resolution

    @classmethod
    def measure_mtime_resolution(cls, mount_point: Path) -> int:
        tmp_file = Path(mount_point) / ".__fileformats_mtime_measurement_test_file__"
        tmp_file.touch()
        try:
            # Get the initial mtime
            initial_mtime = tmp_file.lstat().st_mtime_ns
            # Wait for a very short period and update the mtime using touch
            for sleep_time in [0.001, 0.01, 0.1, 1, 2]:  # 1ms, 10ms, 100ms, 1s
                time.sleep(sleep_time)
                tmp_file.touch()
                new_mtime = tmp_file.lstat().st_mtime_ns
                if new_mtime != initial_mtime:
                    # Calculate the resolution
                    resolution = new_mtime - initial_mtime
                    return resolution
            raise RuntimeError(f"Couldn't determine the mtime for the {mount_point}")
        finally:
            tmp_file.unlink()

    _mount_table: ty.Optional[ty.List[ty.Tuple[str, str]]] = None

    # Define a table of file system types and their mtime resolutions (in seconds)
    FS_MTIME_NS_RESOLUTION: ty.Dict[str, int] = {
        "ext4": 1,  # 1 nanosecond
        "xfs": 1,  # 1 nanosecond
        "btrfs": 1,  # 1 nanosecond
        "ntfs": 100,  # 100 nanoseconds
        "hfs": 1,  # 1 nanosecond
        "apfs": 1,  # 1 nanosecond
        "fat32": int(2e9),  # 2 seconds (2 * 10^9 nanoseconds)
        "exfat": int(1e9),  # 1 second (1 * 10^9 nanoseconds)
        # Add more file systems and their resolutions as needed
    }
