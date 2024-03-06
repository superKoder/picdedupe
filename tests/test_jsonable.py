from typing import Dict
import unittest

from picdeduper import jsonable

class MyClass(jsonable.Jsonable):
    def __init__(self):
        self.name = "John"
        self.age = 42

    def __eq__(self, rhs) -> bool:
        return (self.name == rhs.name) and (self.age == rhs.age)

    def jsonable_encode(self) -> Dict:
        return {
            "name": self.name,
            "age": self.age,
        }
    
    def jsonable_decode(jsonable: Dict):
        obj = MyClass()
        obj.name = jsonable["name"]
        obj.age = jsonable["age"]
        return obj

my_obj = MyClass()

class JsonableEncodeTests(unittest.TestCase):        

    def test_scalars(self):
        self.assertEqual(jsonable.encode(123), 123)
        self.assertEqual(jsonable.encode("hi"), "hi")
        self.assertEqual(jsonable.encode(3.5), 3.5)
        self.assertEqual(jsonable.encode(None), None)

    def test_jsonable(self):
        my_obj = MyClass()
        self.assertDictEqual(jsonable.encode(my_obj), {"name": "John", "age": 42})

    def test_list(self):
        self.assertListEqual(jsonable.encode([7, 8]), [7, 8])
        self.assertListEqual(jsonable.encode(["hello", "world"]), ["hello", "world"])
        self.assertListEqual(jsonable.encode([123, my_obj]), [123, {"name": "John", "age": 42}])

    def test_set(self):
        self.assertListEqual(jsonable.encode({7, 8}), [7, 8])
        self.assertListEqual(jsonable.encode({"hello", "world"}), ["hello", "world"])

    def test_dict(self):
        self.assertDictEqual(jsonable.encode({"one": 1, "two": 2}), {"one": 1, "two": 2})
        self.assertDictEqual(jsonable.encode({"pers": my_obj}), {"pers": {"name": "John", "age": 42}})


class JsonableDecodeTests(unittest.TestCase):        

    def test_scalars(self):
        self.assertEqual(jsonable.decode(123, int), 123)
        self.assertEqual(jsonable.decode("hi", str), "hi")
        self.assertEqual(jsonable.decode(3.5, float), 3.5)
        self.assertEqual(jsonable.decode(None, None), None)

    def test_dict_or_jsonable(self):
        self.assertEqual(jsonable.decode({"name": "John", "age": 42}, MyClass), my_obj)
        self.assertDictEqual(jsonable.decode({"one": 1, "two": 2}, Dict), {"one": 1, "two": 2})

    def test_list(self):
        self.assertListEqual(jsonable.decode([7, 8], list), [7, 8])
        self.assertListEqual(jsonable.decode(["hello", "world"], list), ["hello", "world"])
        self.assertListEqual(jsonable.decode([{"name": "John", "age": 42}], MyClass), [my_obj])

    def test_set(self):
        self.assertSetEqual(jsonable.decode([7, 8], set), {7, 8})
        self.assertSetEqual(jsonable.decode(["hello", "world"], set), {"hello", "world"})
