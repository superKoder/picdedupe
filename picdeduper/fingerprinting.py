from picdeduper import common as pdc
from picdeduper import platform as pds

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


def _image_resolution_string(image_properties: pdc.PropertyDict) -> str:
    if not "kMDItemPixelHeight" in image_properties:
        return None
    if not "kMDItemPixelWidth" in image_properties:
        return None
    res = image_properties["kMDItemPixelHeight"] + "x" + image_properties["kMDItemPixelWidth"]
    if "kMDItemBitsPerSample" in image_properties:
        res += "@" + image_properties["kMDItemBitsPerSample"]
    return res


def _image_location_string(image_properties: pdc.PropertyDict) -> str:
    if not "kMDItemLatitude" in image_properties:
        return None
    if not "kMDItemLongitude" in image_properties:
        return None
    return "<" + image_properties["kMDItemLatitude"] + "," + image_properties["kMDItemLongitude"] + ">"


def _image_creator_string(image_properties: pdc.PropertyDict) -> str:
    creator_parts = []
    for key in MDLS_CREATOR_KEYS:
        if not key in image_properties:
            continue
        creator_parts.append(image_properties[key])
    return "/".join(creator_parts)


def _image_angles_string(image_properties: pdc.PropertyDict) -> str:
    angle_parts = []
    for key in MDLS_ANGLES_KEYS:
        if not key in image_properties:
            continue
        angle_parts.append(image_properties[key])
    return "/".join(angle_parts)


def _image_date_string(image_properties: pdc.PropertyDict) -> str:
    for key in MDLS_IMAGE_DATE_KEYS:
        if key in image_properties:
            return image_properties[key]
    return None


def _file_date_string(image_properties: pdc.PropertyDict) -> str:
    for key in MDLS_FILE_DATE_KEYS:
        if key in image_properties:
            return image_properties[key]
    return None


def _file_size_string(image_properties: pdc.PropertyDict) -> str:
    for key in MDLS_FILE_SIZE_KEYS:
        if key in image_properties:
            return image_properties[key]
    return None


def _image_camera_settings_string(image_properties: pdc.PropertyDict) -> str:
    settings = []
    for key in MDLS_CAMERA_SETTING_KEYS:
        if not key in image_properties:
            continue
        settings.append(image_properties[key])
    return "/".join(settings)


class Fingerprinter:

    def __init__(self, platform: pds.Platform) -> None:
        self.platform = platform
        assert self.platform.is_mac_os()

    def _properties_of_image_file(self, path: pds.Path) -> pdc.PropertyDict:
        """Returns a list of properties that identify the identitiy of a file"""
        params = [["-name", x] for x in MDLS_KEYS]

        cmd = ["mdls"]
        cmd.extend([x for sublist in params for x in sublist])
        cmd.append(path)

        output_dict = dict()
        raw_lines = self.platform.raw_stdout_of(cmd).split(b"\n")
        for raw_line in raw_lines:
            raw_parts = raw_line.split(b"=")
            if len(raw_parts) != 2:
                continue
            if b" (null)" == raw_parts[1]:
                continue
            key = raw_parts[0].decode("utf-8").strip()
            val = raw_parts[1].decode("utf-8").strip().strip("\"")
            output_dict[key] = val

        return output_dict

    def quick_image_signature_dict_of(self, image_path: pds.Path) -> pdc.PropertyDict:
        image_properties = self._properties_of_image_file(image_path)
        return {
            pdc.KEY_FILE_DATE: _file_date_string(image_properties),
            pdc.KEY_FILE_SIZE: _file_size_string(image_properties),
        }

    def image_signature_dict_of(self, image_path: pds.Path) -> pdc.PropertyDict:
        image_properties = self._properties_of_image_file(image_path)
        return {
            pdc.KEY_FILE_CORE_NAME: pds.path_core_filename(image_path),
            pdc.KEY_FILE_HASH: self.platform.quick_file_hash(image_path),
            pdc.KEY_FILE_DATE: _file_date_string(image_properties),
            pdc.KEY_FILE_SIZE: _file_size_string(image_properties),
            pdc.KEY_IMAGE_RES: _image_resolution_string(image_properties),
            pdc.KEY_IMAGE_LOC: _image_location_string(image_properties),
            pdc.KEY_IMAGE_CREATOR: _image_creator_string(image_properties),
            pdc.KEY_IMAGE_DATE: _image_date_string(image_properties),
            pdc.KEY_IMAGE_ANGLES: _image_angles_string(image_properties),
            pdc.KEY_IMAGE_CAMSET: _image_camera_settings_string(image_properties),
        }
