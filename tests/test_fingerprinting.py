import unittest

from picdeduper import platform as pds
from picdeduper import fingerprinting as pdf


class FingerprintTests(unittest.TestCase):

    # TODO: Needs more variations of this test
    def test_quick_image_signature_dict_of(self):
        path = "/test/testfile.tst"
        platform = pds.FakePlatform()
        platform.configure_raw_stdout_of(
            "mdls -name kMDItemFSSize -name kMDItemFSContentChangeDate -name kMDItemFSCreationDate -name kMDItemDateAdded -name kMDItemContentModificationDate -name kMDItemContentCreationDate -name kMDItemAcquisitionModel -name kMDItemCreator -name kMDItemLatitude -name kMDItemLongitude -name kMDItemAltitude -name kMDItemPixelHeight -name kMDItemPixelWidth -name kMDItemBitsPerSample -name kMDItemImageDirection -name kMDItemGPSDestBearing -name kMDItemImageDirection -name kMDItemGPSDestBearing /test/testfile.tst",
            b"""
            kMDItemAcquisitionModel                = "iPhone 11 Pro"
            kMDItemAltitude                        = 12.3
            kMDItemBitsPerSample                   = 24
            kMDItemContentCreationDate             = 2019-12-25 03:12:06 +0000
            kMDItemContentModificationDate         = 2019-12-25 03:12:06 +0000
            kMDItemCreator                         = "13.4"
            kMDItemDateAdded                       = 2022-11-01 08:46:06 +0000
            kMDItemExposureTimeSeconds             = 0.0166
            kMDItemFNumber                         = 1.8
            kMDItemFocalLength                     = 4.25
            kMDItemFSContentChangeDate             = 2019-12-25 03:12:06 +0000
            kMDItemFSCreationDate                  = 2019-12-25 03:12:06 +0000
            kMDItemFSSize                          = 4772278
            kMDItemGPSDestBearing                  = 4.32
            kMDItemImageDirection                  = 5.43
            kMDItemLatitude                        = 123.2323
            kMDItemLongitude                       = 34.4343
            kMDItemPixelHeight                     = 3024
            kMDItemPixelWidth                      = 4032
            """)

        fingerprinter = pdf.Fingerprinter(platform)
        result = fingerprinter.quick_image_signature_dict_of(path)

        self.assertDictEqual(result, {
            "file_date": "2019-12-25 03:12:06 +0000",
            "file_size": "4772278",
        })

    # TODO: Needs more variations of this test
    def test_image_signature_dict_of(self):
        path = "/test/testfile.tst"
        platform = pds.FakePlatform()

        platform.configure_raw_stdout_of(
            "mdls -name kMDItemFSSize -name kMDItemFSContentChangeDate -name kMDItemFSCreationDate -name kMDItemDateAdded -name kMDItemContentModificationDate -name kMDItemContentCreationDate -name kMDItemAcquisitionModel -name kMDItemCreator -name kMDItemLatitude -name kMDItemLongitude -name kMDItemAltitude -name kMDItemPixelHeight -name kMDItemPixelWidth -name kMDItemBitsPerSample -name kMDItemImageDirection -name kMDItemGPSDestBearing -name kMDItemImageDirection -name kMDItemGPSDestBearing /test/testfile.tst",
            b"""
            kMDItemAcquisitionModel                = "iPhone 11 Pro"
            kMDItemAltitude                        = 12.3
            kMDItemBitsPerSample                   = 24
            kMDItemContentCreationDate             = 2019-12-25 03:12:06 +0000
            kMDItemContentModificationDate         = 2019-12-25 03:12:06 +0000
            kMDItemCreator                         = "13.4"
            kMDItemDateAdded                       = 2022-11-01 08:46:06 +0000
            kMDItemExposureTimeSeconds             = 0.0166
            kMDItemFNumber                         = 1.8
            kMDItemFocalLength                     = 4.25
            kMDItemFSContentChangeDate             = 2019-12-25 03:12:06 +0000
            kMDItemFSCreationDate                  = 2019-12-25 03:12:06 +0000
            kMDItemFSSize                          = 4772278
            kMDItemGPSDestBearing                  = 4.32
            kMDItemImageDirection                  = 5.43
            kMDItemLatitude                        = 123.2323
            kMDItemLongitude                       = 34.4343
            kMDItemPixelHeight                     = 3024
            kMDItemPixelWidth                      = 4032
            """)
        platform.configure_raw_stdout_of(
            "openssl sha256 -r /test/testfile.tst",
            b"01234DeadBead9876")

        fingerprinter = pdf.Fingerprinter(platform)
        result = dict()
        fingerprinter.image_signature_dict_of(path, result)

        self.assertDictEqual(result, {
            "file_date": "2019-12-25 03:12:06 +0000",
            "file_size": "4772278",
            "file_hash": "01234DeadBead9876",
            "file_core_name": "testfile",
            "image_angles": "5.43/4.32",
            "image_camset": "0.0166/1.8/4.25",
            "image_creator": "iPhone 11 Pro/13.4",
            "image_date": "2019-12-25 03:12:06 +0000",
            "image_loc": "<123.2323,34.4343>",
            "image_res": "3024x4032@24",
        })
