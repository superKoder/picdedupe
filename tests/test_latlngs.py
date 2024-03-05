import unittest

from picdeduper import latlngs
from picdeduper import jsonable

class LatLngTests(unittest.TestCase):
    def test_init(self):
        latlng1 = latlngs.LatLng(-123.45, +45.678)
        self.assertAlmostEqual(latlng1.latitude, -123.45)
        self.assertAlmostEqual(latlng1.longitude, +45.678)
        self.assertAlmostEqual(latlng1.altitude, 0.0)

        latlng2 = latlngs.LatLng(+123.45, -45.678, +32)
        self.assertAlmostEqual(latlng2.latitude, +123.45)
        self.assertAlmostEqual(latlng2.longitude, -45.678)
        self.assertAlmostEqual(latlng2.altitude, +32.)

    def test_as_string(self):
        latlng1 = latlngs.LatLng(-123.45, +45.678)
        self.assertEqual(latlng1.as_string(), "<-123.45,45.678>")
        self.assertEqual(str(latlng1), "<-123.45,45.678>")

        latlng2 = latlngs.LatLng(+123.45, -45.678)
        self.assertEqual(latlng2.as_string(), "<123.45,-45.678>")
        self.assertEqual(str(latlng2), "<123.45,-45.678>")

    def test_parse_string(self):
        latlng1 = latlngs.parse_latlng("<98.765,123.45>")
        self.assertAlmostEqual(latlng1.latitude, +98.765)
        self.assertAlmostEqual(latlng1.longitude, +123.45)

        latlng2 = latlngs.parse_latlng("<+98.765,-123.45>")
        self.assertAlmostEqual(latlng2.latitude, +98.765)
        self.assertAlmostEqual(latlng2.longitude, -123.45)

        latlng3 = latlngs.parse_latlng("<-98.765,+123.45>")
        self.assertAlmostEqual(latlng3.latitude, -98.765)
        self.assertAlmostEqual(latlng3.longitude, +123.45)

        wrong1 = latlngs.parse_latlng("<hi>")
        self.assertIsNone(wrong1)

    def test_equal(self):
        latlngA1 = latlngs.LatLng(+98.765, -123.45)
        latlngA2 = latlngs.parse_latlng("<+98.765,-123.45>")
        latlngB1 = latlngs.LatLng(-98.765, +123.45)
        latlngB2 = latlngs.parse_latlng("<-98.765,+123.45>")
        self.assertEqual(latlngA1, latlngA2)
        self.assertEqual(latlngA2, latlngA1)
        self.assertEqual(latlngB1, latlngB2)
        self.assertEqual(latlngB2, latlngB1)
        self.assertNotEqual(latlngA1, latlngB1)
        self.assertNotEqual(latlngA1, latlngB2)
        self.assertNotEqual(latlngA2, latlngB1)
        self.assertNotEqual(latlngA2, latlngB2)
        self.assertNotEqual(latlngB1, latlngA1)
        self.assertNotEqual(latlngB1, latlngA2)
        self.assertNotEqual(latlngB2, latlngA1)
        self.assertNotEqual(latlngB2, latlngA2)
        self.assertNotEqual(latlngs.BRUSSELS, latlngs.PARIS)
        self.assertNotEqual(latlngs.LONDON, latlngs.NEW_YORK)
        self.assertFalse(latlngs.BRUSSELS == latlngs.PARIS)
        self.assertFalse(latlngs.LONDON == latlngs.NEW_YORK)

    def test_distance_in_degrees(self):
        latlngA = latlngs.LatLng(+98.765, -123.45)
        latlngB = latlngs.LatLng(+98.765, -124.45)
        latlngC = latlngs.LatLng(+98.764, -123.45)

        self.assertAlmostEqual(latlngA.distance_in_degrees(latlngA), 0.0)
        self.assertAlmostEqual(latlngB.distance_in_degrees(latlngB), 0.0)
        self.assertAlmostEqual(latlngC.distance_in_degrees(latlngC), 0.0)

        self.assertAlmostEqual(latlngA.distance_in_degrees(latlngB), 1.000, places=5)
        self.assertAlmostEqual(latlngA.distance_in_degrees(latlngC), 0.001, places=5)
        self.assertAlmostEqual(latlngB.distance_in_degrees(latlngA), 1.000, places=5)
        self.assertAlmostEqual(latlngB.distance_in_degrees(latlngC), 1.000, places=5)
        self.assertAlmostEqual(latlngC.distance_in_degrees(latlngA), 0.001, places=5)
        self.assertAlmostEqual(latlngC.distance_in_degrees(latlngB), 1.000, places=5)

    def test_distance_in_km(self):
        brussels = latlngs.LatLng(50.8476, 4.3572)
        paris = latlngs.LatLng(48.8566, 2.3522)
        nyc = latlngs.LatLng(40.7128, -74.0060)

        self.assertAlmostEqual(brussels.distance_in_km(brussels), 0.0)
        self.assertAlmostEqual(paris.distance_in_km(paris), 0.0)
        self.assertAlmostEqual(nyc.distance_in_km(nyc), 0.0)

        self.assertAlmostEqual(brussels.distance_in_km(paris), 264, places=0)
        self.assertAlmostEqual(brussels.distance_in_km(nyc), 5896, places=0)
        self.assertAlmostEqual(paris.distance_in_km(brussels), 264, places=0)
        self.assertAlmostEqual(paris.distance_in_km(nyc), 5844, places=0)
        self.assertAlmostEqual(nyc.distance_in_km(brussels), 5896, places=0)
        self.assertAlmostEqual(nyc.distance_in_km(paris), 5844, places=0)

    def test_jsonable_to(self):
        latlng = latlngs.LatLng(+98.765, -124.45)
        self.assertDictEqual(jsonable.to(latlng), {"lat": +98.765, "lng": -124.45})