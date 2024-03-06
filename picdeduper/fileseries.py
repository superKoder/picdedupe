from picdeduper import platform as pds
from picdeduper import common as pdc
from picdeduper import filegroups
from picdeduper import latlngs as pdl
from picdeduper import time as pdt
from picdeduper import images
from picdeduper import jsonable

from abc import ABC, abstractmethod
from typing import List, Dict

KEY_JSON_GROUPS = "groups"
KEY_JSON_FILE_PREFIX = "fileprefix"
KEY_JSON_FILE_NUM = "filenum"
KEY_JSON_LATLNG = "latlng"
KEY_JSON_TIMESTAMP = "timestamp"
KEY_JSON_CREATOR = "creator"


class PictureFileSeries(jsonable.Jsonable):
    """
    A PictureFileSeries is a gap-less sequence of pictures taken at the 
    same time, at the same place, by the same creator.

    In reality, it stores PictureFileGroups, rather than individual files.
    """

    def __init__(self,
                 file_prefix: str,
                 file_num: int,
                 latlng: pdl.LatLng,
                 timestamp: pdt.Timestamp,
                 creator: str,
                 file_groups: List[filegroups.PictureFileGroup] = None) -> None:

        super().__init__()
        self.file_prefix = file_prefix
        self.file_num = file_num
        self.latlng = latlng
        self.timestamp = timestamp
        self.creator = creator
        self.file_groups: List[filegroups.PictureFileGroup] = (file_groups if file_groups else list())

    def add_file_group(self, file_group: filegroups.PictureFileGroup) -> None:
        self.file_groups.append(file_group)

    def jsonable_encode(self) -> Dict:
        return {
            KEY_JSON_FILE_PREFIX: jsonable.encode(self.file_prefix),
            KEY_JSON_FILE_NUM: jsonable.encode(self.file_num),
            KEY_JSON_LATLNG: jsonable.encode(self.latlng),
            KEY_JSON_TIMESTAMP: jsonable.encode(self.timestamp),
            KEY_JSON_CREATOR: jsonable.encode(self.creator),
            KEY_JSON_GROUPS: jsonable.encode(self.file_groups),
        }

    def jsonable_decode(val: dict):
        return PictureFileSeries(
            jsonable.decode(val[KEY_JSON_FILE_PREFIX], str),
            jsonable.decode(val[KEY_JSON_FILE_NUM], int),
            jsonable.decode(val[KEY_JSON_LATLNG], pdl.LatLng),
            jsonable.decode(val[KEY_JSON_TIMESTAMP], pdt.Timestamp),
            jsonable.decode(val[KEY_JSON_CREATOR], str),
            jsonable.decode(val[KEY_JSON_GROUPS], filegroups.PictureFileGroup)
        )


class PictureFileSeriesSplitter:
    """
    Mechanism to split a stream of files (PictureFileGroups) into PictureFileSeries.
    """

    def __init__(self,
                 max_file_num_gap=0,
                 max_distance_degrees=10,
                 max_timestamp_diff: pdt.Timestamp = 8*3600) -> None:

        self.all_file_series: List[PictureFileSeries] = list()

        self.curr_file_series: PictureFileSeries = None
        self.curr_file_group: filegroups.PictureFileGroup = None
        self.curr_file_prefix: str = None
        self.curr_file_num: int = None

        self.max_file_num_gap = max_file_num_gap
        self.max_distance_degrees = max_distance_degrees
        self.max_timestamp_diff = max_timestamp_diff

    def _is_file_num_gap(self, file_prefix: str, file_num: int) -> bool:
        if (not self.curr_file_prefix) or (not self.curr_file_series):
            return True
        if (self.curr_file_prefix != file_prefix):
            return True
        if (file_num <= self.curr_file_num):
            return True
        return (file_num > self.curr_file_num + self.max_file_num_gap + 1)

    def _is_too_far_away(self, latlng: pdl.LatLng) -> bool:
        if self.curr_file_series.latlng == latlng:
            return False
        if not self.curr_file_series:
            return True
        if not latlng:
            return False    # We don't know. So let's look at other fields.
        if not self.curr_file_series.latlng:
            return True
        return ((self.curr_file_series.latlng.distance_in_km(latlng)) > self.max_distance_degrees)

    def _is_too_new(self, timestamp: pdt.Timestamp) -> bool:
        if not self.curr_file_series:
            return True
        if self.curr_file_series.timestamp == timestamp:
            return False
        if not self.curr_file_series.timestamp:
            return True
        return (pdt.seconds_between_times(timestamp, self.curr_file_series.timestamp) > self.max_timestamp_diff)

    def _is_other_creator(self, creator: str) -> bool:
        if not self.curr_file_series:
            return True
        return (self.curr_file_series.creator != creator)

    def _start_new_series(self,
                          file_prefix: str,
                          file_num: int,
                          latlng: pdl.LatLng,
                          timestamp: pdt.Timestamp,
                          creator: str) -> None:
        self.curr_file_series = PictureFileSeries(file_prefix, file_num, latlng, timestamp, creator)
        self.all_file_series.append(self.curr_file_series)

    def _needs_new_series(self,
                          file_prefix: str,
                          file_num: int,
                          latlng: pdl.LatLng,
                          timestamp: pdt.Timestamp,
                          creator: str) -> bool:

        if self._is_file_num_gap(file_prefix, file_num):
            return True

        if self._is_too_far_away(latlng):
            return True

        if self._is_too_new(timestamp):
            return True

        if self._is_other_creator(creator):
            return True

        return False

    def add_path(self,
                 path: pds.Path,
                 properties: pdc.PropertyDict) -> None:

        file_prefix, file_num = images.filename_dcf_prefix_and_number(path)
        creator = properties[pdc.KEY_IMAGE_CREATOR]
        latlng: pdl.LatLng = pdl.parse_latlng(properties[pdc.KEY_IMAGE_LOC])
        timestamp: pdt.Timestamp = pdt.timestamp_from_string(properties[pdc.KEY_IMAGE_DATE])

        if ((self.curr_file_group) and
            (file_num == self.curr_file_num) and
                (self.curr_file_group.could_include_path(path))):
            self.curr_file_group.add_file_path(path)
            return

        if self._needs_new_series(file_prefix, file_num, latlng, timestamp, creator):
            self._start_new_series(file_prefix, file_num, latlng, timestamp, creator)

        assert self.curr_file_series

        self.curr_file_group = filegroups.PictureFileGroup()
        self.curr_file_group.add_file_path(path)
        self.curr_file_series.add_file_group(self.curr_file_group)
        self.curr_file_prefix = file_prefix
        self.curr_file_num = file_num
