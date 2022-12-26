import unittest

from picdeduper import platform as pds


class PlatformTests(unittest.TestCase):

    def test_path_filename(self):
        self.assertEqual(pds.path_filename("file.ext"), "file.ext")
        self.assertEqual(pds.path_filename("/test/testfile.txt"), "testfile.txt")
        self.assertEqual(pds.path_filename("~/.config"), ".config")
        self.assertEqual(pds.path_filename("/User/me"), "me")

    def test_path_join(self):
        self.assertEqual(pds.path_join("/home/john", "file.ext"), "/home/john/file.ext")
        self.assertEqual(pds.path_join("/home/john/", "file.ext"), "/home/john/file.ext")

    def test_filename_ext(self):
        self.assertEqual(pds.filename_ext("file.ext"), ".ext")
        self.assertEqual(pds.filename_ext("/test/testfile.txt"), ".txt")
        self.assertEqual(pds.filename_ext("~/.config"), "")
        self.assertEqual(pds.filename_ext("/User/me"), "")
        self.assertEqual(pds.filename_ext("IMG_1234.JPG"), ".JPG")
        self.assertEqual(pds.filename_ext("old.IMG_1234.JPG"), ".JPG")

    def test_filename_cut_ext(self):
        self.assertEqual(pds.filename_cut_ext("file.ext"), "file")
        self.assertEqual(pds.filename_cut_ext("/test/testfile.txt"), "testfile")
        self.assertEqual(pds.filename_cut_ext("~/.config"), ".config")
        self.assertEqual(pds.filename_cut_ext("/User/me"), "me")
        self.assertEqual(pds.filename_cut_ext("IMG_1234.JPG"), "IMG_1234")
        self.assertEqual(pds.filename_cut_ext("old.IMG_1234.JPG"), "old.IMG_1234")

    def test_original_path_if_copied_path(self):
        self.assertEqual(pds.original_path_if_copied_path("file.ext"), "file.ext")
        self.assertEqual(pds.original_path_if_copied_path("file 1.ext"), "file.ext")
        self.assertEqual(pds.original_path_if_copied_path("file 22.ext"), "file.ext")
        self.assertEqual(pds.original_path_if_copied_path("file copy.ext"), "file.ext")
        self.assertEqual(pds.original_path_if_copied_path("file copy 1.ext"), "file.ext")
        self.assertEqual(pds.original_path_if_copied_path("file copy 22.ext"), "file.ext")

    def test_path_core_filename(self):
        self.assertEqual(pds.path_core_filename("file.ext"), "file")
        self.assertEqual(pds.path_core_filename("file 1.ext"), "file")
        self.assertEqual(pds.path_core_filename("file 22.ext"), "file")
        self.assertEqual(pds.path_core_filename("file copy.ext"), "file")
        self.assertEqual(pds.path_core_filename("file copy 1.ext"), "file")
        self.assertEqual(pds.path_core_filename("file copy 22.ext"), "file")
        self.assertEqual(pds.path_core_filename("/path/to/file.ext"), "file")
        self.assertEqual(pds.path_core_filename("/path/to/file 1.ext"), "file")
        self.assertEqual(pds.path_core_filename("/path/to/file 22.ext"), "file")
        self.assertEqual(pds.path_core_filename("/path/to/file copy.ext"), "file")
        self.assertEqual(pds.path_core_filename("/path/to/file copy 1.ext"), "file")
        self.assertEqual(pds.path_core_filename("/path/to/file copy 22.ext"), "file")

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
