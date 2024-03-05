import unittest

from picdeduper import common as pdc
from picdeduper import fileseries
from picdeduper import latlngs


class FileSeriesTests(unittest.TestCase):

    def test_perfect_series(self):

        splitter = fileseries.PictureFileSeriesSplitter()

        self.assertEqual(len(splitter.all_file_series), 0)

        properties = {
            pdc.KEY_IMAGE_CREATOR: "creator",
            pdc.KEY_IMAGE_LOC: "<+37.4,-120.3>",
            pdc.KEY_IMAGE_DATE: "2022-12-23 20:13:32 -0700"
        }

        splitter.add_path("/path/one/IMG_1001.JPG", properties)
        splitter.add_path("/path/one/IMG_1002.JPG", properties)
        splitter.add_path("/path/one/IMG_1003.JPG", properties)
        splitter.add_path("/path/one/IMG_1004.JPG", properties)
        self.assertEqual(len(splitter.all_file_series), 1)

    def test_with_gap(self):

        splitter = fileseries.PictureFileSeriesSplitter()

        self.assertEqual(len(splitter.all_file_series), 0)

        properties = {
            pdc.KEY_IMAGE_CREATOR: "creator",
            pdc.KEY_IMAGE_LOC: "<+37.4,-120.3>",
            pdc.KEY_IMAGE_DATE: "2022-12-23 20:13:32 -0700"
        }

        splitter.add_path("/path/one/IMG_1001.JPG", properties)
        splitter.add_path("/path/one/IMG_1002.JPG", properties)

        splitter.add_path("/path/one/IMG_1004.JPG", properties)
        splitter.add_path("/path/one/IMG_1005.JPG", properties)

        self.assertEqual(len(splitter.all_file_series), 2)

    def test_different_file_prefix(self):

        splitter = fileseries.PictureFileSeriesSplitter()

        self.assertEqual(len(splitter.all_file_series), 0)

        properties = {
            pdc.KEY_IMAGE_CREATOR: "creator",
            pdc.KEY_IMAGE_LOC: "<+37.4,-120.3>",
            pdc.KEY_IMAGE_DATE: "2022-12-23 20:13:32 -0700"
        }

        splitter.add_path("/path/one/IMG_1001.JPG", properties)
        splitter.add_path("/path/one/IMG_1002.JPG", properties)

        splitter.add_path("/path/one/PIC_1003.JPG", properties)
        splitter.add_path("/path/one/PIC_1004.JPG", properties)

        self.assertEqual(len(splitter.all_file_series), 2)

    def test_different_location(self):

        splitter = fileseries.PictureFileSeriesSplitter()

        self.assertEqual(len(splitter.all_file_series), 0)

        location_a = {
            pdc.KEY_IMAGE_CREATOR: "creator",
            pdc.KEY_IMAGE_LOC: latlngs.PARIS.as_string(),
            pdc.KEY_IMAGE_DATE: "2022-12-23 20:13:32 -0700"
        }

        location_b = {
            pdc.KEY_IMAGE_CREATOR: "creator",
            pdc.KEY_IMAGE_LOC: latlngs.BRUSSELS.as_string(),  # !!!
            pdc.KEY_IMAGE_DATE: "2022-12-23 20:13:32 -0700"
        }

        splitter.add_path("/path/one/IMG_1001.JPG", location_a)
        splitter.add_path("/path/one/IMG_1002.JPG", location_a)
        splitter.add_path("/path/one/IMG_1003.JPG", location_a)

        splitter.add_path("/path/one/IMG_1004.JPG", location_b)
        splitter.add_path("/path/one/IMG_1005.JPG", location_b)

        self.assertEqual(len(splitter.all_file_series), 2)
        file_series_at_paris = splitter.all_file_series[0]
        file_series_at_brussels = splitter.all_file_series[1]
        self.assertEqual(len(file_series_at_paris.file_groups), 3)
        self.assertEqual(len(file_series_at_brussels.file_groups), 2)

    def test_different_time(self):

        splitter = fileseries.PictureFileSeriesSplitter()

        self.assertEqual(len(splitter.all_file_series), 0)

        time_a = {
            pdc.KEY_IMAGE_CREATOR: "creator",
            pdc.KEY_IMAGE_LOC: latlngs.NEW_YORK.as_string(),
            pdc.KEY_IMAGE_DATE: "2022-12-23 20:13:32 -0700"
        }

        time_b = {
            pdc.KEY_IMAGE_CREATOR: "creator",
            pdc.KEY_IMAGE_LOC: latlngs.NEW_YORK.as_string(),
            pdc.KEY_IMAGE_DATE: "2022-12-24 20:13:32 -0700"  # !!!
        }

        splitter.add_path("/path/one/IMG_1001.JPG", time_a)
        splitter.add_path("/path/one/IMG_1002.JPG", time_a)

        splitter.add_path("/path/one/IMG_1003.JPG", time_b)
        splitter.add_path("/path/one/IMG_1004.JPG", time_b)
        splitter.add_path("/path/one/IMG_1005.JPG", time_b)

        self.assertEqual(len(splitter.all_file_series), 2)
        file_series_on_23rd = splitter.all_file_series[0]
        file_series_on_24th = splitter.all_file_series[1]
        self.assertEqual(len(file_series_on_23rd.file_groups), 2)
        self.assertEqual(len(file_series_on_24th.file_groups), 3)

    def test_different_creator(self):

        splitter = fileseries.PictureFileSeriesSplitter()

        self.assertEqual(len(splitter.all_file_series), 0)

        creator_a = {
            pdc.KEY_IMAGE_CREATOR: "creator",
            pdc.KEY_IMAGE_LOC: latlngs.NEW_YORK.as_string(),
            pdc.KEY_IMAGE_DATE: "2022-12-23 20:13:32 -0700"
        }

        creator_b = {
            pdc.KEY_IMAGE_CREATOR: "other",  # !!!
            pdc.KEY_IMAGE_LOC: latlngs.NEW_YORK.as_string(),
            pdc.KEY_IMAGE_DATE: "2022-12-23 20:13:32 -0700"
        }

        splitter.add_path("/path/one/IMG_1001.JPG", creator_a)
        splitter.add_path("/path/one/IMG_1002.JPG", creator_a)
        splitter.add_path("/path/one/IMG_1003.JPG", creator_a)
        splitter.add_path("/path/one/IMG_1004.JPG", creator_a)

        splitter.add_path("/path/one/IMG_1005.JPG", creator_b)

        self.assertEqual(len(splitter.all_file_series), 2)
        file_series_of_creator1 = splitter.all_file_series[0]
        file_series_of_creator2 = splitter.all_file_series[1]
        self.assertEqual(len(file_series_of_creator1.file_groups), 4)
        self.assertEqual(len(file_series_of_creator2.file_groups), 1)
