import unittest

from picdeduper import platform as pds

class PlatformTests(unittest.TestCase):

    def test_is_picture_file(self):
        platform = pds.FakePlatform()
        self.assertTrue(platform.is_picture_file("IMG_1234.JPG"))
        self.assertTrue(platform.is_picture_file("IMG_1234.jpg"))
        self.assertTrue(platform.is_picture_file("IMG_1234.jpeg"))
        self.assertTrue(platform.is_picture_file("IMG_1234.HEIC"))
        self.assertTrue(platform.is_picture_file("IMG_1234.heic"))
        self.assertFalse(platform.is_picture_file("IMG_1234.mov"))
        self.assertFalse(platform.is_picture_file("IMG_1234.MOV"))
        self.assertFalse(platform.is_picture_file("IMG_1234.MP4"))
        self.assertFalse(platform.is_picture_file("IMG_1234.mp4"))
        self.assertFalse(platform.is_picture_file("IMG_1234.MP3"))
        self.assertFalse(platform.is_picture_file("IMG_1234.WAV"))

    def test_is_video_file(self):
        platform = pds.FakePlatform()
        self.assertFalse(platform.is_video_file("IMG_1234.JPG"))
        self.assertFalse(platform.is_video_file("IMG_1234.jpg"))
        self.assertFalse(platform.is_video_file("IMG_1234.jpeg"))
        self.assertFalse(platform.is_video_file("IMG_1234.HEIC"))
        self.assertFalse(platform.is_video_file("IMG_1234.heic"))
        self.assertTrue(platform.is_video_file("IMG_1234.mov"))
        self.assertTrue(platform.is_video_file("IMG_1234.MOV"))
        self.assertTrue(platform.is_video_file("IMG_1234.MP4"))
        self.assertTrue(platform.is_video_file("IMG_1234.mp4"))
        self.assertFalse(platform.is_video_file("IMG_1234.MP3"))
        self.assertFalse(platform.is_video_file("IMG_1234.WAV"))

    def test_is_image_file(self):
        platform = pds.FakePlatform()
        self.assertTrue(platform.is_image_file("IMG_1234.JPG"))
        self.assertTrue(platform.is_image_file("IMG_1234.jpg"))
        self.assertTrue(platform.is_image_file("IMG_1234.jpeg"))
        self.assertTrue(platform.is_image_file("IMG_1234.HEIC"))
        self.assertTrue(platform.is_image_file("IMG_1234.heic"))
        self.assertTrue(platform.is_image_file("IMG_1234.mov"))
        self.assertTrue(platform.is_image_file("IMG_1234.MOV"))
        self.assertTrue(platform.is_image_file("IMG_1234.MP4"))
        self.assertTrue(platform.is_image_file("IMG_1234.mp4"))
        self.assertFalse(platform.is_image_file("IMG_1234.MP3"))
        self.assertFalse(platform.is_image_file("IMG_1234.WAV"))
        self.assertFalse(platform.is_image_file(".IMG_1234.JPG"))
        self.assertFalse(platform.is_image_file(".IMG_1234.HEIC"))

    def test_file_md5_hash(self):
        cmd_line = "md5 -q /test/testfile.tst"
        platform = pds.FakePlatform()
        platform.configure_raw_stdout_of(cmd_line, b"1234DeadBead9876\n")

        output = platform.file_md5_hash("/test/testfile.tst")
        
        self.assertTrue(cmd_line in platform.called_cmd_lines)
        self.assertEqual(output, "1234DeadBead9876")

    def test_file_sha256_hash(self):
        cmd_line = "openssl sha256 -r /test/testfile.tst"
        platform = pds.FakePlatform()
        platform.configure_raw_stdout_of(cmd_line, b"1234DeadBead9876 */test/testfile.tst\n")

        output = platform.file_sha256_hash("/test/testfile.tst")
        
        self.assertTrue(cmd_line in platform.called_cmd_lines)
        self.assertEqual(output, "1234DeadBead9876")
