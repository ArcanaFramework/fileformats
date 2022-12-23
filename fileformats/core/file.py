from __future__ import annotations
import os
from pathlib import Path
import typing as ty
from itertools import chain
from copy import copy
import logging
import shutil
import attrs
from attrs.converters import optional
from .exceptions import (
    FileFormatError,
)
from .base import FileGroup, absolute_path, absolute_paths_dict


logger = logging.getLogger("fileformats")


@attrs.define
class BaseFile(FileGroup):

    is_dir = False

    def set_fs_paths(self, fs_paths: ty.List[Path]):
        self._check_paths_exist(fs_paths)
        fs_path = absolute_path(self.matches_ext(*fs_paths))
        self.exists = True
        self.fs_path = fs_path

    def all_file_paths(self):
        """The paths of all nested files within the file-group"""
        if self.fs_path is None:
            raise RuntimeError(
                f"Attempting to access file paths of {self} before they are set"
            )
        return self.fs_paths

    def copy_to(self, fs_path: str or Path, symlink: bool = False):
        """Copies the file-group to the new path, with auxiliary files saved
        alongside the primary-file path.

        Parameters
        ----------
        path : str
            Path to save the file-group to excluding file extensions
        symlink : bool
            Use symbolic links instead of copying files to new location

        Returns
        -------
        BaseFile
            A copy of the file object at the new file system path
        """
        if symlink:
            copy_file = os.symlink
        else:
            copy_file = shutil.copyfile
        dest_path = Path(str(fs_path) + "." + self.ext)
        copy_file(self.fs_path, dest_path)
        cpy = copy(self)
        cpy.set_fs_paths([dest_path])
        return cpy

    @classmethod
    def copy_ext(cls, old_path, new_path):
        """Copy extension from the old path to the new path, ensuring that all
        of the extension is used (e.g. 'my.gz' instead of 'gz')

        Parameters
        ----------
        old_path: Path or str
            The path from which to copy the extension from
        new_path: Path or str
            The path to append the extension to

        Returns
        -------
        Path
            The new path with the copied extension
        """
        if not cls.matches_ext(old_path):
            raise FileFormatError(
                f"Extension of old path ('{str(old_path)}') does not match that "
                f"of file, '{cls.ext}'"
            )
        suffix = "." + cls.ext if cls.ext is not None else old_path.suffix
        return Path(new_path).with_suffix(suffix)

    @classmethod
    def all_exts(cls):
        return [cls.ext]


@attrs.define
class WithSideCars(BaseFile):
    """Base class for file-groups with a primary file and several header or
    side car files
    """

    side_cars: ty.Dict[str, str] = attrs.field(converter=optional(absolute_paths_dict))

    @side_cars.default
    def default_side_cars(self):
        if self.fs_path is None:
            return {}
        return self.default_side_car_paths(self.fs_path)

    @side_cars.validator
    def validate_side_cars(self, _, side_cars):
        if side_cars:
            if self.fs_path is None:
                raise RuntimeError(
                    "Auxiliary files can only be provided to a FileGroup "
                    f"of '{self.path}' ({side_cars}) if the local path is "
                    "as well"
                )
            if set(self.side_car_exts) != set(side_cars.keys()):
                raise RuntimeError(
                    "Keys of provided auxiliary files ('{}') don't match "
                    "format ('{}')".format(
                        "', '".join(side_cars.keys()), "', '".join(self.side_car_exts)
                    )
                )
            missing_side_cars = [(n, f) for n, f in side_cars.items() if not f.exists()]
            if missing_side_cars:
                msg = (
                    f"Attempting to set paths of auxiliary files for {self} "
                    "that don't exist: "
                )
                for name, fpath in missing_side_cars:
                    if fpath.parent.exists():
                        info = "neighbouring files: " + ", ".join(
                            p.name for p in fpath.parent.iterdir()
                        )
                    else:
                        info = "parent directory doesn't exist"
                    msg += f"\n    {name}: {str(fpath)} - {info}"
                raise RuntimeError(msg)

    @classmethod
    def fs_names(cls):
        """Return names for each top-level file-system path in the file group,
        used when generating Pydra task interfaces.

        Returns
        -------
        tuple[str]
            sequence of names for top-level file-system paths in the file group"""
        return super().fs_names() + cls.side_car_exts

    def set_fs_paths(self, paths: ty.List[Path]):
        super().set_fs_paths(paths)
        to_assign = set(Path(p) for p in paths)
        to_assign.remove(self.fs_path)
        # Begin with default side_car paths and override if provided
        default_side_cars = self.default_side_car_paths(self.fs_path)
        for sc_ext in self.side_car_exts:
            try:
                matched = self.side_cars[sc_ext] = absolute_path(
                    self.matches_ext(*paths, ext=sc_ext)
                )
            except FileFormatError:
                self.side_cars[sc_ext] = default_side_cars[sc_ext]
            else:
                to_assign.remove(matched)

    @property
    def fs_paths(self):
        return chain(super().fs_paths, self.side_cars.values())

    def side_car(self, name):
        return self.side_cars[name]

    def copy_to(self, fs_path: str or Path, symlink: bool = False):
        """Copies the file-group to the new path, with auxiliary files saved
        alongside the primary-file path.

        Parameters
        ----------
        fs_path : str or Path
            Path to save the file-group to excluding file extensions
        symlink : bool
            Use symbolic links instead of copying files to new location
        """
        if symlink:
            copy_file = os.symlink
        else:
            copy_file = shutil.copyfile
        dest_path = Path(str(fs_path) + "." + self.ext)
        copy_file(self.fs_path, dest_path)
        dest_side_cars = self.default_side_car_paths(dest_path)
        for sc_ext, sc_path in self.side_cars.items():
            copy_file(sc_path, dest_side_cars[sc_ext])
        cpy = copy(self)
        cpy.set_fs_paths([dest_path] + list(dest_side_cars.values()))
        return cpy

    @classmethod
    def default_side_car_paths(cls, primary_path):
        """
        Get the default paths for auxiliary files relative to the path of the
        primary file, i.e. the same name as the primary path with a different
        extension

        Parameters
        ----------
        primary_path : str
            Path to the primary file in the file_group

        Returns
        -------
        aux_paths : ty.Dict[str, str]
            A dictionary of auxiliary file names and default paths
        """

        return {
            e: Path(str(primary_path)[: -len(cls.ext)] + e) for e in cls.side_car_exts
        }

    @classmethod
    def copy_ext(cls, old_path, new_path):
        """Copy extension from the old path to the new path, ensuring that all
        of the extension is used (e.g. 'my.gz' instead of 'gz'). If the old
        path extension doesn't match the primary path, the methods loops through
        all side-car extensions and selects the longest matching.

        Parameters
        ----------
        old_path: Path or str
            The path from which to copy the extension from
        new_path: Path or str
            The path to append the extension to

        Returns
        -------
        Path
            The new path with the copied extension
        """
        try:
            # Check to see if the path it matches the primary path extension
            return super().copy_ext(old_path, new_path)
        except FileFormatError:
            pass
        matches = []
        for ext in cls.side_car_exts:
            try:
                cls.matches_ext(old_path, ext=ext)
            except FileFormatError:
                pass
            else:
                matches.append(ext)
        if not matches:
            sc_exts_str = "', '".join(cls.side_car_exts)
            raise FileFormatError(
                f"Extension of old path ('{str(old_path)}') does not match any "
                f" in {cls}: '{cls.ext}', {sc_exts_str}"
            )
        longest_match = max(matches, key=len)
        return Path(new_path).with_suffix("." + longest_match)

    def generalise_checksum_keys(
        self, checksums: ty.Dict[str, str], base_path: Path = None
    ):
        """Generalises the paths used for the file paths in a checksum dictionary
        so that they are the same irrespective of that the top-level file-system
        paths are

        Parameters
        ----------
        checksums: dict[str, str]
            The checksum dict mapping relative file paths to checksums

        Returns
        -------
        dict[str, str]
            The checksum dict with file paths generalised"""
        if base_path is None:
            base_path = self.fs_path
        generalised = {}
        fs_name_dict = {
            self.matches_ext(*checksums.keys(), ext=e): e for e in self.side_car_exts
        }
        mapped_exts = list(fs_name_dict.values())
        duplicates = set([e for e in mapped_exts if mapped_exts.count(e) > 1])
        if duplicates:
            raise RuntimeError(
                f"Multiple files with same extensions found in {self}: "
                + ", ".join(str(k) for k in checksums.keys())
            )
        for key, chksum in checksums.items():
            try:
                rel_key = fs_name_dict[str(key)]
            except KeyError:
                try:
                    rel_key = Path(key).relative_to(base_path)
                except ValueError:
                    continue  # skip these files
            generalised[str(rel_key)] = chksum
        return generalised

    @classmethod
    def all_exts(cls):
        return [cls.ext] + list(cls.side_car_exts)
