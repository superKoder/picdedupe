import unittest

from picdeduper import common as pdc
from picdeduper import evaluation as pde


class EvaluationTests(unittest.TestCase):

    def test_is_consistent_time(self):
        self.assertTrue(pde.is_consistent_time({
            pdc.KEY_IMAGE_DATE: "2022-11-16 22:55:32 -0700",
            pdc.KEY_FILE_DATE: "2022-11-16 22:55:32 -0700",
        }))
        self.assertTrue(pde.is_consistent_time({
            pdc.KEY_IMAGE_DATE: "2022-11-16 22:55:32 -0700",
            pdc.KEY_FILE_DATE: "2022-11-17 07:55:32 +0200",
        }))
        self.assertFalse(pde.is_consistent_time({
            pdc.KEY_IMAGE_DATE: "2022-11-16 22:55:32 -0300",
            pdc.KEY_FILE_DATE: "2022-11-16 22:55:32 +0300",
        }))
