#!/usr/bin/env python

import json
import os
import subprocess
from typing import List, Dict, Set

Filename = str
Path = str
PathList = List[str]
PathSet = Set[str]
CommandLineParts = List[str]
PropertyDict = Dict[str,str]

KEY_FILE_HASH = "file_hash"
KEY_FILE_DATE = "file_date"
KEY_FILE_SIZE = "file_size"
KEY_IMAGE_DATE = "image_date"
KEY_IMAGE_RES = "image_res"
KEY_IMAGE_LOC = "image_loc"
KEY_IMAGE_CREATOR = "image_creator"
KEY_IMAGE_ANGLES = "image_angles"
KEY_IMAGE_CAMSET = "image_camset"

KEY_BY_PATH = "by_path"
KEY_BY_HASH = "by_hash"
KEY_BY_FILENAME = "by_filename"

MDLS_KEYS = []

# File size:
MDLS_FILE_SIZE_KEYS = [
    "kMDItemFSSize",
]
MDLS_KEYS += MDLS_FILE_SIZE_KEYS

# File date (order sensitive!):
MDLS_FILE_DATE_KEYS = [
    "kMDItemFSContentChangeDate", 
    "kMDItemFSCreationDate", 
    "kMDItemDateAdded",
]
MDLS_KEYS += MDLS_FILE_DATE_KEYS

# Image date (order sensitive!):
MDLS_IMAGE_DATE_KEYS = [
    "kMDItemContentModificationDate", 
    "kMDItemContentCreationDate", 
]
MDLS_KEYS += MDLS_IMAGE_DATE_KEYS

# Creator:
MDLS_CREATOR_KEYS = [
    "kMDItemAcquisitionModel", 
    "kMDItemCreator",
] 
MDLS_KEYS += MDLS_CREATOR_KEYS

# Location:
MDLS_LOCATION_KEYS = [
    "kMDItemLatitude", 
    "kMDItemLongitude",
    "kMDItemAltitude",
]
MDLS_KEYS += MDLS_LOCATION_KEYS

# Resolution:
MDLS_RESOLUTION_KEYS = [
    "kMDItemPixelHeight",
    "kMDItemPixelWidth",
    "kMDItemBitsPerSample", 
]
MDLS_KEYS += MDLS_RESOLUTION_KEYS

# Angles:
MDLS_ANGLES_KEYS = [
    "kMDItemImageDirection",
    "kMDItemGPSDestBearing",
]
MDLS_KEYS += MDLS_ANGLES_KEYS

# Camera settings:
MDLS_CAMERA_SETTING_KEYS = [
    "kMDItemExposureTimeSeconds",
    "kMDItemFNumber",
    "kMDItemFocalLength",
]
MDLS_KEYS += MDLS_ANGLES_KEYS


class Evaluation:
    def __init__(self) -> None:
        self.same_filename = list()
        self.same_hash = list()
        self.same_image_properties = list()

    def add_same_filename(self, path: Path):
        self.same_filename.append(path)

    def add_same_hash(self, path: Path):
        self.same_hash.append(path)

    def add_same_image_properties(self, path: Path):
        self.same_image_properties.append(path)

    def paths_with_same_filename(self) -> PathList:
        return self.same_filename

    def paths_with_same_hash(self) -> PathList:
        return self.same_hash

    def paths_with_same_image_properties(self) -> PathList:
        return self.same_image_properties

    def has_filename_dupes(self) -> bool:
        return 0 != len(self.same_filename)

    def has_hash_dupes(self) -> bool:
        return 0 != len(self.same_hash)

    def has_image_property_dupes(self) -> bool:
        return 0 != len(self.same_image_properties)

class IndexStore:

    def __init__(self) -> None:
        self.by_file_path = dict()
        self.by_file_hash = dict()
        self.by_file_name = dict()

    def _path_list_for_hash(self, hash_str: str) -> PathList:
        if not hash_str in self.by_file_hash:
            self.by_file_hash[hash_str] = set()
        return self.by_file_hash[hash_str]

    def _path_list_for_filename(self, filename: Filename) -> PathList:
        if not filename in self.by_file_name:
            self.by_file_name[filename] = set()
        return self.by_file_name[filename]

    def add(self, path: Path, image_properties: PropertyDict):
        self.by_file_path[path] = image_properties
        self._path_list_for_hash(image_properties[KEY_FILE_HASH]).add(path)
        filename = os.path.basename(path)
        self._path_list_for_filename(filename).add(path)

    def _as_dict(self) -> Dict[str,List]: 
        dict_repr = {
            KEY_BY_PATH: self.by_file_path,
            KEY_BY_HASH: self.by_file_hash,
            KEY_BY_FILENAME: self.by_file_name,
        }
        for key in dict_repr[KEY_BY_HASH]:
            dict_repr[KEY_BY_HASH][key] = list(dict_repr[KEY_BY_HASH][key])
        for key in dict_repr[KEY_BY_FILENAME]:
            dict_repr[KEY_BY_FILENAME][key] = list(dict_repr[KEY_BY_FILENAME][key])
        return dict_repr

    def save(self, path) -> str: 
        with open(path, "w") as out_file:
            json.dump(obj=self._as_dict(), fp=out_file, indent=2)

    def load(path):
        index_store = IndexStore()
        if not os.path.exists(path):
            print("WARNING: No JSON file found. Starting new one.")
            return index_store
        with open(path, "r") as in_file:
            index_store_dict = json.load(fp=in_file)
            index_store.by_file_path = index_store_dict[KEY_BY_PATH]
            index_store.by_file_hash = index_store_dict[KEY_BY_HASH]
            index_store.by_file_name = index_store_dict[KEY_BY_FILENAME]
            for key in index_store.by_file_hash:
                index_store.by_file_hash[key] = set(index_store.by_file_hash[key])
            for key in index_store.by_file_name:
                index_store.by_file_name[key] = set(index_store.by_file_name[key])
            return index_store


def is_picture_file(filename: Filename) -> bool:
    ext = os.path.splitext(filename)[1].upper()
    if ext == ".JPG": return True
    if ext == ".HEIC": return True
    if ext == ".JPEG": return True
    return False

def is_video_file(filename: Filename) -> bool:
    ext = os.path.splitext(filename)[1].upper()
    if ext == ".MOV": return True
    if ext == ".MP4": return True
    if ext == ".HEVC": return True
    return False

def is_image_file(filename: Filename) -> bool:
    if filename.startswith("."): return False
    return is_picture_file(filename) or is_video_file(filename)

def _every_image_files_path(io_path_list: PathList, dir_path: Path):
    """Recursive part of every_image_files_path()"""
    for root, subdirs, filenames in os.walk(dir_path):
        for filename in filenames:
            path = root + "/" + filename
            if not is_image_file(filename):
                print(f"info: SKIPPING non-image {path}")
                continue
            io_path_list.append(path)

def every_image_files_path(dir_path: Path) -> PathList:
    """Returns a list of full paths of every .jpg, .heic, etc... file."""
    print('dir = ' + dir_path)
    path_list = list()
    _every_image_files_path(path_list, dir_path)
    return path_list

def _raw_stdout_of(cmd_parts: CommandLineParts) -> str:
    """Returns stdout of command line, in raw bytes"""
    return subprocess.run(cmd_parts, stdout=subprocess.PIPE).stdout

def _stdout_of(cmd_parts: CommandLineParts) -> str:
    """Returns stringified version of _byte_stdout_of()"""
    return _raw_stdout_of(cmd_parts).decode("utf-8").strip()

def _file_md5_mac(path: Path) -> str:
    """macOS specific command line to get an MD5 of a file."""
    return _stdout_of(["md5", "-q", path])

def file_md5(path: Path) -> str:
    return _file_md5_mac(path)

def _properties_of_image_file(path: Path) -> PropertyDict:
    """Returns a list of properties that identify the identitiy of a file"""
    params = [["-name", x] for x in MDLS_KEYS]

    cmd = ["mdls"]
    cmd.extend([x for sublist in params for x in sublist])
    cmd.append(path)
    print(" ".join(cmd))

    output_dict = dict()
    raw_lines = _raw_stdout_of(cmd).split(b"\n")
    for raw_line in raw_lines:
        raw_parts = raw_line.split(b"=")
        if len(raw_parts) != 2: continue
        if b" (null)" == raw_parts[1]: continue
        key = raw_parts[0].decode("utf-8").strip()
        val = raw_parts[1].decode("utf-8").strip().strip("\"")
        output_dict[key] = val

    return output_dict

def _image_resolution_string(image_properties: PropertyDict) -> str:
    if not "kMDItemPixelHeight" in image_properties: return None
    if not "kMDItemPixelWidth" in image_properties: return None
    res = image_properties["kMDItemPixelHeight"] + "x" + image_properties["kMDItemPixelWidth"]
    if "kMDItemBitsPerSample" in image_properties:
        res += "@" + image_properties["kMDItemBitsPerSample"]
    return res

def _image_location_string(image_properties: PropertyDict) -> str:
    if not "kMDItemLatitude" in image_properties: return None
    if not "kMDItemLongitude" in image_properties: return None
    return "<" + image_properties["kMDItemLatitude"] + "," + image_properties["kMDItemLongitude"] + ">"

def _image_creator_string(image_properties: PropertyDict) -> str:
    creator_parts = []
    for key in MDLS_CREATOR_KEYS:
        if not key in image_properties: continue
        creator_parts.append(image_properties[key])
    return "/".join(creator_parts)

def _image_angles_string(image_properties: PropertyDict) -> str:
    angle_parts = []
    for key in MDLS_ANGLES_KEYS:
        if not key in image_properties: continue
        angle_parts.append(image_properties[key])
    return "/".join(angle_parts)

def _image_date_string(image_properties: PropertyDict) -> str:
    for key in MDLS_IMAGE_DATE_KEYS:
        if key in image_properties:
            return image_properties[key]
    return None

def _file_date_string(image_properties: PropertyDict) -> str:
    for key in MDLS_FILE_DATE_KEYS:
        if key in image_properties:
            return image_properties[key]
    return None

def _file_size_string(image_properties: PropertyDict) -> str:
    for key in MDLS_FILE_SIZE_KEYS:
        if key in image_properties:
            return image_properties[key]
    return None

def _image_camera_settings_string(image_properties: PropertyDict) -> str:
    settings = []
    for key in MDLS_CAMERA_SETTING_KEYS:
        if not key in image_properties: continue
        settings.append(image_properties[key])
    return "/".join(settings)

def quick_image_signature_dict_of(image_path: Path) -> PropertyDict:
    image_properties = _properties_of_image_file(image_path)
    return {
        KEY_FILE_DATE : _file_date_string(image_properties),
        KEY_FILE_SIZE : _file_size_string(image_properties),
    }

def image_signature_dict_of(image_path: Path) -> PropertyDict:
    image_properties = _properties_of_image_file(image_path)
    return {
        KEY_FILE_HASH : file_md5(image_path),
        KEY_FILE_DATE : _file_date_string(image_properties),
        KEY_FILE_SIZE : _file_size_string(image_properties),
        KEY_IMAGE_RES : _image_resolution_string(image_properties),
        KEY_IMAGE_LOC : _image_location_string(image_properties),
        KEY_IMAGE_CREATOR : _image_creator_string(image_properties),
        KEY_IMAGE_DATE : _image_date_string(image_properties),
        KEY_IMAGE_ANGLES : _image_angles_string(image_properties),
        KEY_IMAGE_CAMSET : _image_camera_settings_string(image_properties),
    }

def is_quick_signature_equal(image_path: Path, index_store: IndexStore) -> bool:
    """
    Returns True if the image's quick signature matches the one we have in the JSON-loaded results. 
    This assumes that no changes were made to the file. 
    This is not necessarily true, though! A hash should be used for certainty.
    """
    if not image_path in index_store.by_file_path:
        return False
    quick_signature = quick_image_signature_dict_of(image_path)
    if quick_signature[KEY_FILE_SIZE] != index_store.by_file_path[image_path][KEY_FILE_SIZE]: return False
    if quick_signature[KEY_FILE_DATE] != index_store.by_file_path[image_path][KEY_FILE_DATE]: return False
    return True

def _is_equal_property(key: str, a: PropertyDict, b: PropertyDict) -> bool:
    return ((key in a) == (key in b)) and (a[key] == b[key])

def evaluate(candidate_image_path: Path, candidate_image_properties: PropertyDict, index_store: IndexStore) -> Evaluation:
    evaluation = Evaluation()
    candidate_image_filename = os.path.basename(candidate_image_path)
    for image_path in index_store.by_file_name:
        
        image_filename = os.path.basename(image_path)
        if candidate_image_filename == image_filename: 
            evaluation.add_same_filename(image_path)

        image_properties = index_store.by_file_name[image_path]
        if _is_equal_property(KEY_FILE_HASH, candidate_image_properties, image_properties):
            evaluation.add_same_hash(image_path)

        if (_is_equal_property(KEY_IMAGE_RES, candidate_image_properties, image_properties) and
            _is_equal_property(KEY_IMAGE_DATE, candidate_image_properties, image_properties) and
            _is_equal_property(KEY_IMAGE_CREATOR, candidate_image_properties, image_properties) and
            _is_equal_property(KEY_IMAGE_LOC, candidate_image_properties, image_properties) and
            _is_equal_property(KEY_IMAGE_ANGLES, candidate_image_properties, image_properties)):
            evaluation.add_same_image_properties(image_path)

    return evaluation

def is_likely_file_dupe(evaluation: Evaluation, out_paths: PathList) -> bool:
    if not evaluation.has_hash_dupes(): return False
    out_paths.clear()
    out_paths.extend(evaluation.paths_with_same_hash())
    return True

def is_likely_image_dupe(evaluation: Evaluation, out_paths: PathList) -> bool:
    if not evaluation.has_image_property_dupes(): return False
    out_paths.clear()
    out_paths.extend(evaluation.paths_with_same_image_properties())
    return True

def main():
    JSON_FILENAME = "picdedupe.json"
    # START_DIR = "/Users/tim/AllPics.copy/bronmateriaal"
    START_DIR = "/Users/tim/Tim11pro/_KEEP"

    index_store = IndexStore.load(JSON_FILENAME)
    out_paths = list()

    all_image_paths = every_image_files_path(START_DIR)
    for image_path in all_image_paths:
        print(f"FILE: {image_path}")

        if is_quick_signature_equal(image_path, index_store):
            print(f"SKIPPING UNTOUCHED {image_path}")
            continue

        image_properties = image_signature_dict_of(image_path)
        evaluation = evaluate(image_path, image_properties, index_store)

        # TODO: Make evaluation() aware of weak data
        # TODO: Detect .mov for .jpg (on creator + date + filename?)

        if is_likely_file_dupe(evaluation, out_paths):
            print(f"DUPE: {image_path} is a file dupe of {out_paths}")
            # TODO: IF DUPE *AND* SAME:
            # TODO:   Move to ./DUPES
            # TODO:   Add a ./DUPES/{filename}.txt with the original

        if is_likely_image_dupe(evaluation, out_paths):
            print(f"SAME: {image_path} is an image dupe of {out_paths}")

            # TODO: IF "better version" of same filename minus ext:
            # TODO:   Add(replace) file in same path
            # TODO:   Rename worse version as filename.heic.jpg
            # TODO:   Move to ./ENHANCEMENTS

            # TODO: If differently named (or not better):
            # TODO:   Move to ./SIMILAR
            # TODO:   Add a ./SIMILAR/{filename}.txt with original

        index_store.add(image_path, image_properties)

    index_store.save(JSON_FILENAME)

if __name__ == "__main__":
    main()
