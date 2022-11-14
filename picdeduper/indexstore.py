import json
from typing import Dict, List

from picdeduper import common as pdc
from picdeduper import platform as pds


class IndexStore:

    def __init__(self, platform: pds.Platform) -> None:
        self.platform = platform
        self.by_path = dict()
        self.by_hash = dict()
        self.by_core_filename = dict()

    def _pathset_for_hash(self, hash_str: str) -> pds.PathSet:
        if not hash_str in self.by_hash:
            self.by_hash[hash_str] = set()
        return self.by_hash[hash_str]

    def _pathset_for_core_filename(self, filename: pds.Filename) -> pds.PathSet:
        if not filename in self.by_core_filename:
            self.by_core_filename[filename] = set()
        return self.by_core_filename[filename]

    def add(self, path: pds.Path, image_properties: pdc.PropertyDict):
        self.by_path[path] = image_properties
        self._pathset_for_hash(image_properties[pdc.KEY_FILE_HASH]).add(path)
        # filename = pds.filename_cut_ext(pds.filename_likely_original(pds.path_filename(path)))
        core_filename = pds.path_core_filename(path)
        self._pathset_for_core_filename(core_filename).add(path)

    def _as_dict(self) -> Dict[str, List]:
        by_path_copy = self.by_path  # avoiding redundant copy
        by_hash_copy = dict()
        by_filename_copy = dict()
        for key, val in self.by_hash.items():
            by_hash_copy[key] = sorted(val)
        for key, val in self.by_core_filename.items():
            by_filename_copy[key] = sorted(val)
        return {
            pdc.KEY_BY_PATH: by_path_copy,
            pdc.KEY_BY_HASH: by_hash_copy,
            pdc.KEY_BY_FILENAME: by_filename_copy,
        }

    def save(self, path: pds.Path) -> str:
        json_string = json.dumps(obj=self._as_dict(), indent=2, sort_keys=True)
        self.platform.write_text_file(path, json_string)

    def load(path: pds.Path, platform: pds.Platform) -> None:
        index_store = IndexStore(platform)
        if not platform.path_exists(path):
            print("WARNING: No JSON file found. Starting new one.")
            return index_store
        content = platform.read_text_file(path)
        index_store_dict = json.loads(content)
        index_store.by_path = index_store_dict[pdc.KEY_BY_PATH]
        index_store.by_hash = index_store_dict[pdc.KEY_BY_HASH]
        index_store.by_core_filename = index_store_dict[pdc.KEY_BY_FILENAME]
        for key in index_store.by_hash:
            index_store.by_hash[key] = set(index_store.by_hash[key])
        for key in index_store.by_core_filename:
            index_store.by_core_filename[key] = set(index_store.by_core_filename[key])
        return index_store


def load(path: pds.Path) -> None:
    return IndexStore.load(path)
