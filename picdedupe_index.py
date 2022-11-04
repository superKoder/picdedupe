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
        self.same_filename = set()
        self.same_hash = set()
        self.same_image_properties = set()

    def add_same_filename(self, path: Path):
        self.same_filename.add(path)

    def add_same_hash(self, path: Path):
        self.same_hash.add(path)

    def add_same_image_properties(self, path: Path):
        self.same_image_properties.add(path)

    def paths_with_same_filename(self) -> PathSet:
        return self.same_filename

    def paths_with_same_hash(self) -> PathSet:
        return self.same_hash

    def paths_with_same_image_properties(self) -> PathSet:
        return self.same_image_properties

    def has_filename_dupes(self) -> bool:
        return 0 != len(self.same_filename)

    def has_hash_dupes(self) -> bool:
        return 0 != len(self.same_hash)

    def has_image_property_dupes(self) -> bool:
        return 0 != len(self.same_image_properties)

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
        filename = os.path.basename(path)
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
            index_store.by_path = index_store_dict[KEY_BY_PATH]
            index_store.by_hash = index_store_dict[KEY_BY_HASH]
            index_store.by_filename = index_store_dict[KEY_BY_FILENAME]
            for key in index_store.by_hash:
                index_store.by_hash[key] = set(index_store.by_hash[key])
            for key in index_store.by_filename:
                index_store.by_filename[key] = set(index_store.by_filename[key])
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
                print(f"Skipping non-image: {path}")
                continue
            io_path_list.append(path)

def every_image_files_path(dir_path: Path) -> PathList:
    """Returns a list of full paths of every .jpg, .heic, etc... file."""
    path_list = list()
    _every_image_files_path(path_list, dir_path)
    return path_list

def _raw_stdout_of(cmd_parts: CommandLineParts) -> str:
    """Returns stdout of command line, in raw bytes"""
    return subprocess.run(cmd_parts, stdout=subprocess.PIPE).stdout

def _stdout_of(cmd_parts: CommandLineParts) -> str:
    """Returns stringified version of _byte_stdout_of()"""
    return _raw_stdout_of(cmd_parts).decode("utf-8").strip()

def file_md5(path: Path) -> str:
    # WARNING: This is macOS specific! On Linux, it is md5sum.
    return _stdout_of(["md5", "-q", path])

def _properties_of_image_file(path: Path) -> PropertyDict:
    """Returns a list of properties that identify the identitiy of a file"""
    params = [["-name", x] for x in MDLS_KEYS]

    cmd = ["mdls"]
    cmd.extend([x for sublist in params for x in sublist])
    cmd.append(path)

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
    if not image_path in index_store.by_path:
        return False
    quick_signature = quick_image_signature_dict_of(image_path)
    if quick_signature[KEY_FILE_SIZE] != index_store.by_path[image_path][KEY_FILE_SIZE]: return False
    if quick_signature[KEY_FILE_DATE] != index_store.by_path[image_path][KEY_FILE_DATE]: return False
    return True

def _is_equal_property(key: str, a: PropertyDict, b: PropertyDict) -> bool:
    return ((key in a) == (key in b)) and (a[key] == b[key])

def evaluate(candidate_image_path: Path, candidate_image_properties: PropertyDict, index_store: IndexStore) -> Evaluation:
    evaluation = Evaluation()

    candidate_hash = candidate_image_properties[KEY_FILE_HASH]
    candidate_filename = os.path.basename(candidate_image_path)

    if candidate_hash in index_store.by_hash:
        evaluation.paths_with_same_hash().update(index_store.by_hash[candidate_hash])

    if candidate_filename in index_store.by_filename:
        evaluation.paths_with_same_filename().update(index_store.by_filename[candidate_filename])

    for other_image_path, other_image_properties in index_store.by_path.items():
        
        if (_is_equal_property(KEY_IMAGE_RES, candidate_image_properties, other_image_properties) and
            _is_equal_property(KEY_IMAGE_DATE, candidate_image_properties, other_image_properties) and
            _is_equal_property(KEY_IMAGE_CREATOR, candidate_image_properties, other_image_properties) and
            _is_equal_property(KEY_IMAGE_LOC, candidate_image_properties, other_image_properties) and
            _is_equal_property(KEY_IMAGE_ANGLES, candidate_image_properties, other_image_properties)):
            evaluation.add_same_image_properties(other_image_path)

    return evaluation


def _index_dir(index_store: IndexStore, start_dir: Path, skip_untouched=True, do_evaluation=True):

    print(f"Indexing from {start_dir}...")

    all_image_paths = every_image_files_path(start_dir)
    for image_path in all_image_paths:
        if skip_untouched and is_quick_signature_equal(image_path, index_store):
            print(f"Skipping untouched: {image_path}")
            continue

        print(f"Processing image: {image_path}")
        image_properties = image_signature_dict_of(image_path)

        if do_evaluation:
            evaluation = evaluate(image_path, image_properties, index_store)

            # TODO: Make evaluation() aware of weak data
            # TODO: Detect .mov for .jpg (on creator + date + filename?)

            if evaluation.has_hash_dupes():
                print(f"! DUPE ! {image_path} is a file dupe of {evaluation.paths_with_same_hash()}")
                # TODO: IF DUPE *AND* SAME:
                # TODO:   Move to ./DUPES
                # TODO:   Add a ./DUPES/{filename}.txt with the original

            if evaluation.has_image_property_dupes():
                print(f"? SAME ? {image_path} is an image dupe of {evaluation.paths_with_same_image_properties()}")

                # TODO: IF "better version" of same filename minus ext:
                # TODO:   Add(replace) file in same path
                # TODO:   Rename worse version as filename.heic.jpg
                # TODO:   Move to ./ENHANCEMENTS

                # TODO: If differently named (or not better):
                # TODO:   Move to ./SIMILAR
                # TODO:   Add a ./SIMILAR/{filename}.txt with original

        index_store.add(image_path, image_properties)
    print(f"Indexing of {start_dir} is done.")


def index_established_collection_dir(index_store: IndexStore, start_dir: Path):
    _index_dir(
        index_store, 
        start_dir, 
        skip_untouched=True, 
        do_evaluation=False,
        )

def evaluate_candidate_dir(index_store: IndexStore, start_dir: Path):
    _index_dir(
        index_store, 
        start_dir, 
        skip_untouched=False, 
        do_evaluation=True,
        )


class FixItDescriptionElement:
    def __init__(self, text: str) -> None:
        self.text = text
    def text(self):
        return self.text
    def has_link(self) -> bool:
        pass # abstract
    def link(self) -> str:
        pass # abstract

class FixItDescriptionTextElement(FixItDescriptionElement):
    def has_link(self) -> bool:
        return False
    def link(self) -> str:
        return None

class FixItDescriptionBoldTextElement(FixItDescriptionElement):
    def has_link(self) -> bool:
        return False
    def link(self) -> str:
        return None

class FixItDescriptionFilePathElement(FixItDescriptionElement):
    def __init__(self, path: Path, label: str) -> None:
        super().__init__(path)
        self.path = path
        self.label = label
    def has_link(self) -> bool:
        return True
    def link(self) -> str:
        return "file://" + self.path
    def label(self) -> str:
        return self.label

class FixItDescription:
    def __init__(self) -> None:
        self.elements = list()
    def add(self, element: FixItDescriptionElement):
        self.elements.append(element)
    def add_text(self, text: str):
        self.add(FixItDescriptionTextElement(text))
    def add_bold_text(self, text: str):
        self.add(FixItDescriptionBoldTextElement(text))
    def add_file_path(self, path: Path, label: str):
        self.add(FixItDescriptionFilePathElement(path, label))
    def as_simple_text(self) -> str:
        return " ".join([x.text() for x in self.elements])

class FixItAction:
    def __init__(self) -> None:
        self.description = FixItDescription()
    def describe(self) -> FixItDescription:
        return self.description
    def doIt(self) -> bool:
        return True

class FixItMoveFileAction(FixItAction):
    """Moves a file to another location"""
    def __init__(self, path: Path, to_dir: Path) -> None:
        super().__init__()
        self.path = path
        self.to_dir = to_dir
        self.description.add_bold_text("Move")
        self.description.add_file_path(path)
        self.description.add_text("to directory")
        self.description.add_file_path(to_dir)

    def doIt(self, add_explanation=True) -> bool:
        from_path = os.path.join(self.from_dir, self.filename)
        to_path = os.path.join(self.to_dir, self.filename)
        cmd = ["echo", "mv", from_path, to_path]
        _stdout_of(cmd)

class FixIt:
    def __init__(self) -> None:
        self.description = FixItDescription()
        self.actions = list()
    
    def describe(self) -> FixItDescription:
        return self.description()
    
    def proposed_actions(self) -> List[FixItAction]:
        return self.actions
    
    def ignore(self) -> None:
        pass

class ExactDupeFixIt(FixIt):
    def __init__(self, candidate_path: Path, other_path: Path) -> None:
        super().__init__()
        self.description.add_text("Detected an")
        self.description.add_bold_text("exact dupe")
        self.description.add_text("at")
        self.description.add_file_path(candidate_path)
        self.description.add_text("matching")
        self.description.add_file_path(other_path)
        self.actions.append(FixItMoveFileAction(candidate_path, "./_dupes"))

class WrongDateFixIt(FixIt):
    pass

class SimilarImageFixIt(FixIt):
    pass

class BetterQualityVersionFixIt(SimilarImageFixIt):
    """e.g. Found a new HEIC of a JPEG"""
    pass

class WorseQualityVersionFixIt(SimilarImageFixIt):
    """e.g. Found a new JPEG of an HEIC"""
    pass

class SmallerVersionFixIt(SimilarImageFixIt):
    """e.g. A cropped version of an original"""
    pass

class BiggerVersionFixIt(SimilarImageFixIt):
    """e.g. A cropped version of an original"""
    pass

def main():
    JSON_FILENAME = "picdedupe.json"
    COLLECTION_START_DIR = "/Users/tim/AllPics.copy/bronmateriaal"
    CANDIDATE_START_DIR = "/Users/tim/Tim11pro"

    print(f"Will load IndexStore from {JSON_FILENAME} if available.")
    index_store = IndexStore.load(JSON_FILENAME)
    print("Done.")

    print(f"Indexing collection at {COLLECTION_START_DIR}...")
    index_established_collection_dir(index_store, COLLECTION_START_DIR)
    print("Done.")

    print(f"Saving IndexStore to {JSON_FILENAME}...")
    index_store.save(JSON_FILENAME)
    print("Done.")

    print(f"Checking candidates at {CANDIDATE_START_DIR}...")
    evaluate_candidate_dir(index_store, CANDIDATE_START_DIR)
    print("Done.")

if __name__ == "__main__":
    main()
