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
    e.g. "README.TXT"   -> None
    """
    core_filename = pds.path_core_filename(path)
    if len(core_filename) != 8:
        return None
    matches = RE_FILENAME_NUM.match(core_filename)
    if matches:
        prefix = matches.group(1)
        ordering = int(matches.group(2))
        return (prefix, ordering)
    return None
