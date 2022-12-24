import unittest

from picdeduper import images


class TimeTests(unittest.TestCase):

    def test_filename_dcf_prefix_and_number(self):
        self.assertEqual(images.filename_dcf_prefix_and_number("IMG_1234.JPG"), ("IMG_", 1234))
        self.assertEqual(images.filename_dcf_prefix_and_number("DSC_1234.JPG"), ("DSC_", 1234))
        self.assertEqual(images.filename_dcf_prefix_and_number("DSC01234.JPG"), ("DSC0", 1234))
        self.assertEqual(images.filename_dcf_prefix_and_number("P1230123.JPG"), ("P123",  123))

        self.assertEqual(images.filename_dcf_prefix_and_number("IMG_1234 copy.JPG"), ("IMG_", 1234))
        self.assertEqual(images.filename_dcf_prefix_and_number("IMG_1234 copy 2.JPG"), ("IMG_", 1234))
        self.assertEqual(images.filename_dcf_prefix_and_number("IMG_1234 2.JPG"), ("IMG_", 1234))

        self.assertEqual(images.filename_dcf_prefix_and_number("MyPic.JPG"), None)
        self.assertEqual(images.filename_dcf_prefix_and_number("My1stPic.JPG"), None)
        self.assertEqual(images.filename_dcf_prefix_and_number("NotDsc12345.JPG"), None)
