from picdeduper import platform as pds

import re

from typing import Tuple

RE_FILENAME_NUM = re.compile(r"^(.{4})(\d{4})$")


def filename_dcf_prefix_and_number(path) -> Tuple[str, int]:
    """
    Cuts a DCF filename into a prefix and order number.
    https://en.wikipedia.org/wiki/Design_rule_for_Camera_File_system

    e.g. "IMG_1234.JPG" -> ("IMG_", 1234)  # Canon, Apple
    e.g. "DSC_1234.JPG" -> ("DSC_", 1234)  # Nikon, Sony
    e.g. "DSCF1234.JPG" -> ("DSCF", 1234)  # Fuji
    e.g. "P0010123.JPG" -> ("P001",  123)  # Panasonic
    e.g. "README.TXT"   -> (None  , None)
    """
    core_filename = pds.path_core_filename(path)
    if len(core_filename) != 8:
        return (None, None)
    matches = RE_FILENAME_NUM.match(core_filename)
    if matches:
        prefix = matches.group(1)
        ordering = int(matches.group(2))
        return (prefix, ordering)
    return (None, None)

def is_picture_filename(filename: pds.Filename) -> bool:
    ext = pds.filename_ext(filename).upper()
    if ext == ".JPG":
        return True
    if ext == ".HEIC":
        return True
    if ext == ".JPEG":
        return True
    return False

def is_video_filename(filename: pds.Filename) -> bool:
    ext = pds.filename_ext(filename).upper()
    if ext == ".MOV":
        return True
    if ext == ".MP4":
        return True
    if ext == ".HEVC":
        return True
    return False

def is_image_filename(filename: pds.Filename) -> bool:
    if filename.startswith("."):
        return False
    return is_picture_filename(filename) or is_video_filename(filename)

def every_image_path(platform: pds.Platform, start_dir: pds.Path) -> pds.PathList:
    """
    Returns full paths to all .jpg, .heic, .mov, etc... files under `start_dir`.
    It scans recursively, and sorts the filenames per subdirectory.
    """
    return platform.every_file_path(start_dir, is_image_filename)