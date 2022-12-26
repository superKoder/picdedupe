import unittest

from picdeduper import images
from picdeduper import platform as pds

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

    def test_is_picture_file(self):
        self.assertTrue(images.is_picture_filename("IMG_1234.JPG"))
        self.assertTrue(images.is_picture_filename("IMG_1234.jpg"))
        self.assertTrue(images.is_picture_filename("IMG_1234.jpeg"))
        self.assertTrue(images.is_picture_filename("IMG_1234.HEIC"))
        self.assertTrue(images.is_picture_filename("IMG_1234.heic"))
        self.assertFalse(images.is_picture_filename("IMG_1234.mov"))
        self.assertFalse(images.is_picture_filename("IMG_1234.MOV"))
        self.assertFalse(images.is_picture_filename("IMG_1234.MP4"))
        self.assertFalse(images.is_picture_filename("IMG_1234.mp4"))
        self.assertFalse(images.is_picture_filename("IMG_1234.MP3"))
        self.assertFalse(images.is_picture_filename("IMG_1234.WAV"))

    def test_is_video_file(self):
        self.assertFalse(images.is_video_filename("IMG_1234.JPG"))
        self.assertFalse(images.is_video_filename("IMG_1234.jpg"))
        self.assertFalse(images.is_video_filename("IMG_1234.jpeg"))
        self.assertFalse(images.is_video_filename("IMG_1234.HEIC"))
        self.assertFalse(images.is_video_filename("IMG_1234.heic"))
        self.assertTrue(images.is_video_filename("IMG_1234.mov"))
        self.assertTrue(images.is_video_filename("IMG_1234.MOV"))
        self.assertTrue(images.is_video_filename("IMG_1234.MP4"))
        self.assertTrue(images.is_video_filename("IMG_1234.mp4"))
        self.assertFalse(images.is_video_filename("IMG_1234.MP3"))
        self.assertFalse(images.is_video_filename("IMG_1234.WAV"))

    def test_is_image_file(self):
        self.assertTrue(images.is_image_filename("IMG_1234.JPG"))
        self.assertTrue(images.is_image_filename("IMG_1234.jpg"))
        self.assertTrue(images.is_image_filename("IMG_1234.jpeg"))
        self.assertTrue(images.is_image_filename("IMG_1234.HEIC"))
        self.assertTrue(images.is_image_filename("IMG_1234.heic"))
        self.assertTrue(images.is_image_filename("IMG_1234.mov"))
        self.assertTrue(images.is_image_filename("IMG_1234.MOV"))
        self.assertTrue(images.is_image_filename("IMG_1234.MP4"))
        self.assertTrue(images.is_image_filename("IMG_1234.mp4"))
        self.assertFalse(images.is_image_filename("IMG_1234.MP3"))
        self.assertFalse(images.is_image_filename("IMG_1234.WAV"))
        self.assertFalse(images.is_image_filename(".IMG_1234.JPG"))
        self.assertFalse(images.is_image_filename(".IMG_1234.HEIC"))
