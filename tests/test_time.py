import unittest

from picdeduper import time as pdt


class TimeTests(unittest.TestCase):

    def test_datetime_for_string(self):
        dt = pdt.datetime_from_string("2019-06-30 23:17:38 +0200")
        self.assertEqual(dt.day, 30)
        self.assertEqual(dt.month, 6)
        self.assertEqual(dt.year, 2019)
        self.assertEqual(dt.hour, 23)
        self.assertEqual(dt.minute, 17)
        self.assertEqual(dt.second, 38)

    def test_timestamp_for_string(self):
        ts1 = pdt.timestamp_from_string("2019-06-30 23:17:38 +0200")
        ts2 = pdt.timestamp_from_string("2019-06-30 23:17:38 +0300")
        ts3 = pdt.timestamp_from_string("2019-06-30 21:17:38 +0000")
        self.assertEqual(ts1 - ts2, 3600)
        self.assertEqual(ts1, ts3)

    def test_string_for_timestamp(self):
        self.assertEqual(pdt.string_from_timestamp(1561929458), "2019-06-30 21:17:38 +0000")

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


    def test_seconds_between_times(self):
        a_string = "2022-12-23 22:30:35 -0700"
        b_string = "2022-12-23 22:32:15 -0700"
        a_timestamp = pdt.timestamp_from_string(a_string)
        b_timestamp = pdt.timestamp_from_string(b_string)
        a_datetime = pdt.datetime_from_string(a_string)
        b_datetime = pdt.datetime_from_string(b_string)
        self.assertEqual(pdt.seconds_between_times(a_timestamp, a_timestamp), 0)
        self.assertEqual(pdt.seconds_between_times(b_timestamp, b_timestamp), 0)
        self.assertEqual(pdt.seconds_between_times(a_timestamp, b_timestamp), 100)
        self.assertEqual(pdt.seconds_between_times(b_timestamp, a_timestamp), 100)
        self.assertEqual(pdt.seconds_between_times(a_datetime, b_datetime), 100)
        self.assertEqual(pdt.seconds_between_times(a_string, b_string), 100)
