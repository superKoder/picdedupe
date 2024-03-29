import unittest

from picdeduper import filegroups
from picdeduper import jsonable


class PictureFileGroupTests(unittest.TestCase):

    def test_add_file_single(self):
        filegroup = filegroups.PictureFileGroup()
        filegroup.add_file_path("/test/IMG_123.JPG")
        self.assertEqual(filegroup.main_file_path(), "/test/IMG_123.JPG")
        self.assertEqual(filegroup.all_files(), {"/test/IMG_123.JPG"})

    def test_add_file_jpg_heic(self):
        filegroup = filegroups.PictureFileGroup()
        filegroup.add_file_path("/test/IMG_123.JPG")
        filegroup.add_file_path("/test/IMG_123.HEIC")
        self.assertEqual(filegroup.main_file_path(), "/test/IMG_123.HEIC")
        self.assertEqual(filegroup.all_files(), {"/test/IMG_123.HEIC", "/test/IMG_123.JPG"})

    def test_add_file_heic_jpg(self):
        filegroup = filegroups.PictureFileGroup()
        filegroup.add_file_path("/test/IMG_123.HEIC")
        filegroup.add_file_path("/test/IMG_123.JPG")
        self.assertEqual(filegroup.main_file_path(), "/test/IMG_123.HEIC")
        self.assertEqual(filegroup.all_files(), {"/test/IMG_123.HEIC", "/test/IMG_123.JPG"})

    def test_add_file_jpg_mov(self):
        filegroup = filegroups.PictureFileGroup()
        filegroup.add_file_path("/test/IMG_123.JPG")
        filegroup.add_file_path("/test/IMG_123.MOV")
        self.assertEqual(filegroup.main_file_path(), "/test/IMG_123.JPG")
        self.assertEqual(filegroup.all_files(), {"/test/IMG_123.JPG", "/test/IMG_123.MOV"})

    def test_add_file_mov_jpg(self):
        filegroup = filegroups.PictureFileGroup()
        filegroup.add_file_path("/test/IMG_123.MOV")
        filegroup.add_file_path("/test/IMG_123.JPG")
        self.assertEqual(filegroup.main_file_path(), "/test/IMG_123.JPG")
        self.assertEqual(filegroup.all_files(), {"/test/IMG_123.JPG", "/test/IMG_123.MOV"})

    def test_add_file_mov_jpg_heic(self):
        filegroup = filegroups.PictureFileGroup()
        filegroup.add_file_path("/test/IMG_123.MOV")
        filegroup.add_file_path("/test/IMG_123.JPG")
        filegroup.add_file_path("/test/IMG_123.HEIC")
        self.assertEqual(filegroup.main_file_path(), "/test/IMG_123.HEIC")
        self.assertEqual(filegroup.all_files(), {"/test/IMG_123.HEIC", "/test/IMG_123.JPG", "/test/IMG_123.MOV"})

    def test_could_include_path(self):
        filegroup = filegroups.PictureFileGroup()
        self.assertFalse(filegroup.could_include_path(None))

        self.assertTrue(filegroup.could_include_path("/test/IMG_123.MOV"))
        filegroup.add_file_path("/test/IMG_123.MOV")
        self.assertTrue(filegroup.could_include_path("/test/IMG_123.JPG"))
        filegroup.add_file_path("/test/IMG_123.JPG")
        self.assertTrue(filegroup.could_include_path("/test/IMG_123.HEIC"))
        filegroup.add_file_path("/test/IMG_123.HEIC")

        self.assertFalse(filegroup.could_include_path("/test/IMG_666.HEIC"))

    def test_jsonable_to(self):
        filegroup = filegroups.PictureFileGroup()
        filegroup.add_file_path("/test/IMG_123.MOV")
        filegroup.add_file_path("/test/IMG_123.JPG")
        filegroup.add_file_path("/test/IMG_123.RAW")
        self.assertDictEqual(jsonable.encode(filegroup), {'main': '/test/IMG_123.JPG', 'supporting': ['/test/IMG_123.MOV', '/test/IMG_123.RAW']})

    def test_jsonable_decode(self):
        expected = filegroups.PictureFileGroup()
        expected.add_file_path("/test/IMG_123.MOV")
        expected.add_file_path("/test/IMG_123.JPG")
        expected.add_file_path("/test/IMG_123.RAW")

        input = {'main': '/test/IMG_123.JPG', 'supporting': ['/test/IMG_123.MOV', '/test/IMG_123.RAW']}
        output: filegroups.PictureFileGroup = jsonable.decode(input, filegroups.PictureFileGroup)

        self.assertEqual(output, expected)
