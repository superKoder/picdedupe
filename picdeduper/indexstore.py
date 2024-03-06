import json
from typing import Dict, List

from picdeduper import common as pdc
from picdeduper import platform as pds
from picdeduper import fileseries as pfs
from picdeduper import jsonable

# TODO: This file desperately needs unit tests!!


class IndexStoreData(jsonable.Jsonable):

    def __init__(self) -> None:
        self.by_path = dict()
        self.by_hash = dict()
        self.by_core_filename = dict()
        self.oldest_image_date = "9999-99-99 99:99:99 +9999"
        self.newest_image_date = "0000-00-00 00:00:00 +0000"

    def _pathset_for_hash(self, hash_str: str) -> pds.PathSet:
        if not hash_str in self.by_hash:
            self.by_hash[hash_str] = set()
        return self.by_hash[hash_str]

    def _pathset_for_core_filename(self, filename: pds.Filename) -> pds.PathSet:
        if not filename in self.by_core_filename:
            self.by_core_filename[filename] = set()
        return self.by_core_filename[filename]

    def add(self, path: pds.Path, image_properties: pdc.PropertyDict):
        print(f"Indexed: {path}")
        image_date = image_properties[pdc.KEY_IMAGE_DATE]
        if image_date:
            self.oldest_image_date = min(self.oldest_image_date, image_date)
            self.newest_image_date = max(self.newest_image_date, image_date)
        self.by_path[path] = image_properties
        self._pathset_for_hash(image_properties[pdc.KEY_FILE_HASH]).add(path)
        core_filename = pds.path_core_filename(path)
        self._pathset_for_core_filename(core_filename).add(path)

    def image_properties_for_path(self, path: pds.Path) -> pdc.PropertyDict:
        if not path in self.by_path:
            self.by_path[path] = dict()
        return self.by_path[path]

    def image_properties_dict_for_paths(self, paths: pds.PathSet) -> Dict[pds.Path, pdc.PropertyDict]:
        output: Dict[pds.Path, pdc.PropertyDict] = dict()
        for path in paths:
            output[path] = self.image_properties_for_path(path)
        return output

    def __eq__(self, rhs: object) -> bool:
        return (
            # TODO: self.file_series_splitter = pfs.PictureFileSeriesSplitter()
            self.by_path == rhs.by_path and
            self.by_hash == rhs.by_hash and
            self.by_core_filename == rhs.by_core_filename and
            self.oldest_image_date == rhs.oldest_image_date and
            self.newest_image_date == rhs.newest_image_date
        )

    def jsonable_encode(self) -> Dict[str, List]:
        by_path_copy = self.by_path  # avoiding redundant copy
        by_hash_copy = dict()
        by_filename_copy = dict()
        for key, val in self.by_hash.items():
            by_hash_copy[key] = jsonable.encode(sorted(val))
        for key, val in self.by_core_filename.items():
            by_filename_copy[key] = jsonable.encode(sorted(val))
        return {
            pdc.KEY_BY_PATH: jsonable.encode(by_path_copy),
            pdc.KEY_BY_HASH: jsonable.encode(by_hash_copy),
            pdc.KEY_BY_FILENAME: jsonable.encode(by_filename_copy),
            pdc.KEY_IMAGE_DATE_STATS: jsonable.encode({
                pdc.KEY_OLDEST: self.oldest_image_date,
                pdc.KEY_NEWEST: self.newest_image_date,
            }),
        }

    def jsonable_decode(val: Dict):
        # TODO: This method is not up to date!!
        obj = IndexStoreData()
        obj.by_path = val[pdc.KEY_BY_PATH]
        obj.by_hash = val[pdc.KEY_BY_HASH]
        obj.by_core_filename = val[pdc.KEY_BY_FILENAME]
        image_date_stats = val[pdc.KEY_IMAGE_DATE_STATS]
        obj.newest_image_date = image_date_stats[pdc.KEY_NEWEST]
        obj.oldest_image_date = image_date_stats[pdc.KEY_OLDEST]
        for key in obj.by_hash:
            obj.by_hash[key] = set(obj.by_hash[key])
        for key in obj.by_core_filename:
            obj.by_core_filename[key] = set(obj.by_core_filename[key])
        # NOTE: KEY_BY_SERIES gets loaded through calls ot the splitter.
        return obj


class IndexStore:

    def __init__(self, platform: pds.Platform) -> None:
        self.platform = platform
        self.data = IndexStoreData()
        self.file_series_splitter = pfs.PictureFileSeriesSplitter()

    def add(self, path: pds.Path, image_properties: pdc.PropertyDict):
        print(f"Indexed: {path}")
        self.data.add(path, image_properties)
        self.file_series_splitter.add_path(path, image_properties)

    def image_properties_for_path(self, path: pds.Path) -> pdc.PropertyDict:
        return self.data.image_properties_for_path(path)

    def image_properties_dict_for_paths(self, paths: pds.PathSet) -> Dict[pds.Path, pdc.PropertyDict]:
        return self.data.image_properties_dict_for_paths(paths)

    def save(self, path: pds.Path) -> str:

        # by_series_copy = list()
        # for val in self.file_series_splitter.all_file_series:
        #     by_series_copy.append(jsonable.encode(val))

        storage_dict = jsonable.encode(self.data)
        storage_dict[pdc.KEY_BY_SERIES] = jsonable.encode(sorted(self.file_series_splitter.all_file_series))

        json_string = json.dumps(obj=storage_dict, indent=2, sort_keys=True)
        self.platform.write_text_file(path, json_string)

    def load(path: pds.Path, platform: pds.Platform) -> None:
        index_store = IndexStore(platform)
        if not platform.path_exists(path):
            print("WARNING: No JSON file found. Starting new one.")
            return index_store
        content = platform.read_text_file(path)
        index_store_data_dict = json.loads(content)
        index_store.data = jsonable.decode(index_store_data_dict, IndexStoreData)

        # Rebuild self.file_series_splitter.all_file_series:
        for path, properties in index_store.data.by_path.items():
            index_store.file_series_splitter.add_path(path, properties)

        return index_store


def load(path: pds.Path) -> None:
    return IndexStore.load(path)
