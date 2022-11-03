#!/usr/bin/env python

import json
import os
import subprocess
from typing import List, Dict

KEY_FILE_HASH = "file_hash"
KEY_FILE_DATE = "file_date"
KEY_FILE_SIZE = "file_size"
KEY_IMAGE_DATE = "image_date"
KEY_IMAGE_RES = "image_res"
KEY_IMAGE_LOC = "image_loc"
KEY_IMAGE_CREATOR = "image_creator"
KEY_IMAGE_ANGLES = "image_angles"
KEY_IMAGE_CAMSET = "image_camset"

SAME_FILENAME = "SAME_FILENAME"
SAME_HASH = "SAME_HASH"
SAME_IMAGE_PROP = "SAME_IMAGE_PROP"

def is_picture_file(filename) -> bool:
    ext = os.path.splitext(filename)[1].upper()
    if ext == ".JPG": return True
    if ext == ".HEIC": return True
    if ext == ".JPEG": return True
    return False

def is_video_file(filename) -> bool:
    # ext = os.path.splitext(filename)[1].upper()
    # if ext == ".MOV": return True
    # if ext == ".MP4": return True
    # if ext == ".HEVC": return True
    return False

def is_image_file(filename) -> bool:
    if filename.startswith("."): return False
    return is_picture_file(filename) or is_video_file(filename)

def _every_image_files_path(path_list, dir) -> None:
    """Recursive part of every_image_files_path()"""
    for root, subdirs, filenames in os.walk(dir):
        for filename in filenames:
            path = root + "/" + filename
            if not is_image_file(filename):
                print(f"info: SKIPPING non-image {path}")
                continue
            path_list.append(path)

def every_image_files_path(dir) -> List[str]:
    """Returns a list of full paths of every .jpg, .heic, etc... file."""
    print('dir = ' + dir)
    path_list = list()
    _every_image_files_path(path_list, dir)
    return path_list

def _raw_stdout_of(cmd_parts) -> str:
    # Returns stdout of command line, in raw bytes
    return subprocess.run(cmd_parts, stdout=subprocess.PIPE).stdout

def _stdout_of(cmd_parts) -> str:
    # Returns stringified version of _byte_stdout_of()
    return _raw_stdout_of(cmd_parts).decode("utf-8").strip()

def _file_md5_mac(path) -> str:
    """macOS specific command line to get an MD5 of a file."""
    return _stdout_of(["md5", "-q", path])

def file_md5(path) -> str:
    return _file_md5_mac(path)

def _properties_of_image_file(path) -> Dict[str,str]:
    """Returns a list of properties that identify the identitiy of a file"""
    MDLS_KEYS = [
        
        # File size:
        "kMDItemFSSize",

        # File date:
        "kMDItemFSContentChangeDate", 
        "kMDItemFSCreationDate", 
        "kMDItemDateAdded"

        # Image date:
        "kMDItemContentModificationDate", 
        "kMDItemContentCreationDate", 

        # Creator:
        "kMDItemAcquisitionModel", 
        "kMDItemCreator", 

        # Location:
        "kMDItemLatitude", 
        "kMDItemLongitude",
        "kMDItemAltitude",

        # Resolution:
        "kMDItemPixelHeight",
        "kMDItemPixelWidth",
        "kMDItemBitsPerSample", 

        # Angles:
        "kMDItemImageDirection",
        "kMDItemGPSDestBearing",

        # Camera settings:
        "kMDItemExposureTimeSeconds",
        "kMDItemFNumber",
        "kMDItemFocalLength",
    ]

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

def _image_resolution_string(image_properties: Dict[str,str]) -> str:
    if not "kMDItemPixelHeight" in image_properties: return None
    if not "kMDItemPixelWidth" in image_properties: return None
    res = image_properties["kMDItemPixelHeight"] + "x" + image_properties["kMDItemPixelWidth"]
    if "kMDItemBitsPerSample" in image_properties:
        res += "@" + image_properties["kMDItemBitsPerSample"]
    return res

def _image_location_string(image_properties: Dict[str,str]) -> str:
    if not "kMDItemLatitude" in image_properties: return None
    if not "kMDItemLongitude" in image_properties: return None
    return "<" + image_properties["kMDItemLatitude"] + "," + image_properties["kMDItemLongitude"] + ">"

def _image_creator_string(image_properties: Dict[str,str]) -> str:
    if not "kMDItemAcquisitionModel" in image_properties: return None
    creator = image_properties["kMDItemAcquisitionModel"]
    if "kMDItemCreator" in image_properties:
        creator += "/" + image_properties["kMDItemCreator"]
    return creator

def _image_angles_string(image_properties: Dict[str,str]) -> str:
    angles = ""
    if "kMDItemGPSDestBearing" in image_properties:
        angles += image_properties["kMDItemGPSDestBearing"]
    if "kMDItemImageDirection" in image_properties:
        if len(angles): angles += "/"
        angles += image_properties["kMDItemImageDirection"]
    return angles

def _image_date_string(image_properties: Dict[str,str]) -> str:
    PREFERRED_KEYS_IN_ORDER = [
        "kMDItemContentModificationDate", 
        "kMDItemContentCreationDate", 
    ]
    for key in PREFERRED_KEYS_IN_ORDER:
        if key in image_properties:
            return image_properties[key]
    return None

def _file_date_string(image_properties: Dict[str,str]) -> str:
    PREFERRED_KEYS_IN_ORDER = [
        "kMDItemFSContentChangeDate", 
        "kMDItemFSCreationDate", 
        "kMDItemDateAdded"
    ]
    for key in PREFERRED_KEYS_IN_ORDER:
        if key in image_properties:
            return image_properties[key]
    return None

def _file_size_string(image_properties: Dict[str,str]) -> str:
    PREFERRED_KEYS_IN_ORDER = [
        "kMDItemFSSize", 
    ]
    for key in PREFERRED_KEYS_IN_ORDER:
        if key in image_properties:
            return image_properties[key]
    return None

def _image_camera_settings_string(image_properties: Dict[str,str]) -> str:
    settings = []
    for key in ["kMDItemExposureTimeSeconds", "kMDItemFNumber", "kMDItemFocalLength",]:
        if not key in image_properties: continue
        settings.append(image_properties[key])
    return "/".join(settings)

def quick_image_signature_dict_of(image_path: str) -> Dict[str,str]:
    image_properties = _properties_of_image_file(image_path)
    return {
        KEY_FILE_DATE : _file_date_string(image_properties),
        KEY_FILE_SIZE : _file_size_string(image_properties),
    }

def image_signature_dict_of(image_path: str) -> Dict[str,str]:
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

def save_results_to_json_filename(results_dict: Dict[str,Dict[str,str]], json_output_filename: str):
    with open(json_output_filename, "w") as output_file:
        json.dump(obj=results_dict, fp=output_file, indent=2)

def load_results_from_json_filename(json_input_filename: str) -> Dict[str,Dict[str,str]]:
    if not os.path.exists(json_input_filename):
        print("WARNING: No JSON file found. Starting new one.")
        return dict()
    with open(json_input_filename, "r") as input_file:
        return json.load(fp=input_file)

def is_quick_signature_equal(image_path: str, results_dict: Dict[str,Dict[str,str]]) -> bool:
    """
    Returns True if the image's quick signature matches the one we have in the JSON-loaded results. 
    This assumes that no changes were made to the file. 
    This is not necessarily true, though! A hash should be used for certainty.
    """
    if not image_path in results_dict:
        return False
    quick_signature = quick_image_signature_dict_of(image_path)
    if quick_signature[KEY_FILE_SIZE] != results_dict[image_path][KEY_FILE_SIZE]: return False
    if quick_signature[KEY_FILE_DATE] != results_dict[image_path][KEY_FILE_DATE]: return False
    return True

def _is_equal_property(key: str, a: Dict[str,str], b: Dict[str,str]) -> bool:
    return ((key in a) == (key in b)) and (a[key] == b[key])

def evaluate(candidate_image_path: str, candidate_image_properties: Dict[str,str], results_dict: Dict[str,Dict[str,str]]) -> Dict[str,List[str]]:
    evaluation = {
        SAME_FILENAME : [],
        SAME_HASH : [],
        SAME_IMAGE_PROP : [],
    }
    candidate_image_filename = os.path.basename(candidate_image_path)
    for image_path in results_dict:
        
        image_filename = os.path.basename(image_path)
        if candidate_image_filename == image_filename: 
            evaluation[SAME_FILENAME].append(image_path)

        image_properties = results_dict[image_path]
        if _is_equal_property(KEY_FILE_HASH, candidate_image_properties, image_properties):
            evaluation[SAME_HASH].append(image_path)

        if (_is_equal_property(KEY_IMAGE_RES, candidate_image_properties, image_properties) and
            _is_equal_property(KEY_IMAGE_DATE, candidate_image_properties, image_properties) and
            _is_equal_property(KEY_IMAGE_CREATOR, candidate_image_properties, image_properties) and
            _is_equal_property(KEY_IMAGE_LOC, candidate_image_properties, image_properties) and
            _is_equal_property(KEY_IMAGE_ANGLES, candidate_image_properties, image_properties)):
            evaluation[SAME_IMAGE_PROP].append(image_path)

    return evaluation

def is_likely_file_dupe(evaluation: Dict[str, List[str]], out_paths: List[str]):
    if not len(evaluation[SAME_HASH]): return False
    out_paths.clear()
    out_paths.extend(evaluation[SAME_HASH])
    return True

def is_likely_image_dupe(evaluation: Dict[str, List[str]], out_paths: List[str]):
    if not len(evaluation[SAME_IMAGE_PROP]): return False
    out_paths.clear()
    out_paths.extend(evaluation[SAME_IMAGE_PROP])
    return True

def main():
    JSON_FILENAME = "picdedupe.json"
    # START_DIR = "/Users/tim/AllPics.copy/bronmateriaal"
    START_DIR = "/Users/tim/Tim11pro/_KEEP"

    results_dict = load_results_from_json_filename(JSON_FILENAME)
    out_paths = list()

    all_image_paths = every_image_files_path(START_DIR)
    for image_path in all_image_paths:
        print(f"FILE: {image_path}")

        if is_quick_signature_equal(image_path, results_dict):
            print(f"SKIPPING UNTOUCHED {image_path}")
            continue

        image_properties = image_signature_dict_of(image_path)
        evaluation = evaluate(image_path, image_properties, results_dict)

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

        results_dict[image_path] = image_properties

    # save_results_to_json_filename(results_dict, JSON_FILENAME)

    print ("hi from main")

if __name__ == "__main__":
    main()
