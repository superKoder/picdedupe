import unittest

from picdeduper import time as pdt

class TimeTests(unittest.TestCase):

    def test_datetime_for_string(self):
        dt = pdt.datetime_for_string("2019-06-30 23:17:38 +0200")
        self.assertEqual(dt.day, 30)
        self.assertEqual(dt.month, 6)
        self.assertEqual(dt.year, 2019)
        self.assertEqual(dt.hour, 23)
        self.assertEqual(dt.minute, 17)
        self.assertEqual(dt.second, 38)

    def test_timestamp_for_string(self):
        ts1 = pdt.timestamp_for_string("2019-06-30 23:17:38 +0200")
        ts2 = pdt.timestamp_for_string("2019-06-30 23:17:38 +0300")
        ts3 = pdt.timestamp_for_string("2019-06-30 21:17:38 +0000")
        self.assertEqual(ts1 - ts2, 3600)
        self.assertEqual(ts1, ts3)

    def test_string_for_timestamp(self):
        self.assertEqual(pdt.string_for_timestamp(1561929458), "2019-06-30 21:17:38 +0000")

    def test_time_strings_are_same_time(self):
        self.assertTrue(pdt.time_strings_are_same_time(
            "2019-06-30 23:17:38 +0200",
            "2019-06-30 23:17:38 +0200",
        ))
        self.assertFalse(pdt.time_strings_are_same_time(
            "2019-06-30 23:17:38 +0000",
            "2019-06-30 23:17:38 +0200",
        ))
        self.assertTrue(pdt.time_strings_are_same_time(
            "2019-06-30 21:17:38 +0000",
            "2019-06-30 23:17:38 +0200",
        ))

