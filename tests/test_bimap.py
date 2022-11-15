import unittest

from picdeduper.bimap import BiMap

class BiMapTests(unittest.TestCase):

    def test_setitem(self):
        bimap = BiMap()
        bimap["one"] = 1
        bimap[2] = "two"
        self.assertTrue(1 in bimap)
        self.assertTrue(2 in bimap)
        self.assertTrue("one" in bimap)
        self.assertTrue("two" in bimap)
        self.assertEqual(bimap[1], "one")
        self.assertEqual(bimap[2], "two")
        self.assertEqual(bimap["one"], 1)
        self.assertEqual(bimap["two"], 2)

    def test_delitem(self):
        bimap = BiMap()
        bimap["one"] = 1
        bimap[2] = "two"
        bimap["three"] = 3
        self.assertTrue(1 in bimap)
        self.assertTrue(2 in bimap)
        self.assertTrue(3 in bimap)
        self.assertTrue("one" in bimap)
        self.assertTrue("two" in bimap)
        self.assertTrue("three" in bimap)

        del bimap["three"]
        self.assertTrue(1 in bimap)
        self.assertTrue(2 in bimap)
        self.assertTrue("one" in bimap)
        self.assertTrue("two" in bimap)
        self.assertFalse(3 in bimap)
        self.assertFalse("three" in bimap)

        del bimap[1]
        self.assertTrue(2 in bimap)
        self.assertTrue("two" in bimap)
        self.assertFalse(1 in bimap)
        self.assertFalse(3 in bimap)
        self.assertFalse("one" in bimap)
        self.assertFalse("three" in bimap)

    def test_init(self):
        bimap = BiMap({
            1: "one",
            2: "two",
        })
        self.assertEqual(len(bimap), 4)
        self.assertTrue(1 in bimap)
        self.assertTrue(2 in bimap)
        self.assertTrue("one" in bimap)
        self.assertTrue("two" in bimap)
        self.assertEqual(bimap[1], "one")
        self.assertEqual(bimap[2], "two")
        self.assertEqual(bimap["one"], 1)
        self.assertEqual(bimap["two"], 2)
