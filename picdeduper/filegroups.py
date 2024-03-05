from picdeduper import platform as pds
from picdeduper import jsonable

from abc import ABC, abstractmethod
from typing import Dict

KEY_JSON_MAIN = "main"
KEY_JSON_SUPPORTING = "supporting"

class FileGroup(jsonable.Jsonable):
    """A file group is one or more files that belong together. 
    For example, a .JPG and a .MOV that make up a "live photo" on iOS. Or a .JPG and its RAW."""

    def __init__(self) -> None:
        self.main_path: pds.Path = None
        self.supporting_file_paths: pds.PathSet = set()

    @abstractmethod
    def _determine_main_file_path(self, path: pds.Path) -> pds.Path:
        pass

    def _remove_supporting_file_path(self, path: pds.Path) -> None:
        """Because Python's default Set sucks"""
        if path in self.supporting_file_paths:
            self.supporting_file_paths.remove(path)

    def add_file_path(self, path: pds.Path) -> None:
        new_main_file_path = self._determine_main_file_path(path)
        if self.main_path != new_main_file_path:
            if self.main_path:
                self.supporting_file_paths.add(self.main_path)
            self._remove_supporting_file_path(new_main_file_path)
            self.main_path = new_main_file_path
        if new_main_file_path != path:
            self.supporting_file_paths.add(path)

    def main_file_path(self) -> pds.Path:
        return self.main_path

    def all_files(self) -> pds.PathSet:
        all_files = self.supporting_file_paths
        all_files.add(self.main_path)
        return all_files

    def could_include_path(self, path: pds.Path) -> bool:
        """Only returns True if the filename could potentially belong in this group"""
        if not path:
            return False
        if not self.main_path:
            return True
        return (pds.path_core_filename(self.main_file_path()) ==
                pds.path_core_filename(path))
    
    def as_jsonable(self) -> Dict:
        return {
            KEY_JSON_MAIN: jsonable.to(self.main_path),
            KEY_JSON_SUPPORTING: jsonable.to(sorted(self.supporting_file_paths)),
        }


class PictureFileGroup(FileGroup):
    """A file group is one or more files that belong together. 
    For example, a .JPG and a .MOV that make up a "live photo" on iOS. Or a .JPG and its RAW."""

    def _determine_main_file_path(self, path: pds.Path) -> pds.Path:
        if not self.main_path:
            return path
        main_file_ext = pds.filename_ext(self.main_path).lower()
        this_file_ext = pds.filename_ext(path).lower()
        if this_file_ext != main_file_ext:
            if main_file_ext == '.heic':
                return self.main_path
            if this_file_ext == '.heic':
                return path
            if main_file_ext in ('.jpg', '.jpeg'):
                if this_file_ext in ('.mov', '.mp4'):
                    return self.main_path
            if this_file_ext in ('.jpg', '.jpeg'):
                if main_file_ext in ('.mov', '.mp4'):
                    return path
        return self.main_path
