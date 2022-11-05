from picdeduper.common import *
import picdeduper.system
import json

class IndexStore:

    def __init__(self) -> None:
        self.by_path = dict()
        self.by_hash = dict()
        self.by_filename = dict()

    def _path_set_for_hash(self, hash_str: str) -> PathSet:
        if not hash_str in self.by_hash:
            self.by_hash[hash_str] = set()
        return self.by_hash[hash_str]

    def _path_set_for_filename(self, filename: Filename) -> PathSet:
        if not filename in self.by_filename:
            self.by_filename[filename] = set()
        return self.by_filename[filename]

    def add(self, path: Path, image_properties: PropertyDict):
        self.by_path[path] = image_properties
        self._path_set_for_hash(image_properties[KEY_FILE_HASH]).add(path)
        filename = picdeduper.system.PathFilename(path)
        self._path_set_for_filename(filename).add(path)

    def _as_dict(self) -> Dict[str,List]: 
        by_path_copy = self.by_path # avoiding redundant copy
        by_hash_copy = dict()
        by_filename_copy = dict()
        for key, val in self.by_hash.items():
            by_hash_copy[key] = list(val)
        for key, val in self.by_filename.items():
            by_filename_copy[key] = list(val)
        return {
            KEY_BY_PATH: by_path_copy,
            KEY_BY_HASH: by_hash_copy,
            KEY_BY_FILENAME: by_filename_copy,
        }

    def save(self, path: Path) -> str: 
        with open(path, "w") as out_file:
            json.dump(obj=self._as_dict(), fp=out_file, indent=2, sort_keys=True)

    def load(path: Path) -> None:
        index_store = IndexStore()
        if not picdeduper.system.PathExists(path):
            print("WARNING: No JSON file found. Starting new one.")
            return index_store
        with open(path, "r") as in_file:
            index_store_dict = json.load(fp=in_file)
            index_store.by_path = index_store_dict[KEY_BY_PATH]
            index_store.by_hash = index_store_dict[KEY_BY_HASH]
            index_store.by_filename = index_store_dict[KEY_BY_FILENAME]
            for key in index_store.by_hash:
                index_store.by_hash[key] = set(index_store.by_hash[key])
            for key in index_store.by_filename:
                index_store.by_filename[key] = set(index_store.by_filename[key])
            return index_store

def load(path: Path) -> None:
    return IndexStore.load(path)
