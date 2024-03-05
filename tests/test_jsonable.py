from typing import Dict
import unittest

from picdeduper import jsonable

class MyClass(jsonable.Jsonable):
    def __init__(self):
        self.name = "John"
        self.age = 42

    def as_jsonable(self) -> Dict:
        return {
            "name": self.name,
            "age": self.age,
        }

my_obj = MyClass()

class JsonableTests(unittest.TestCase):        

    def test_scalars(self):
        self.assertEqual(jsonable.to(123), 123)
        self.assertEqual(jsonable.to("hi"), "hi")
        self.assertEqual(jsonable.to(3.5), 3.5)
        self.assertEqual(jsonable.to(None), None)

    def test_jsonable(self):
        my_obj = MyClass()
        self.assertDictEqual(jsonable.to(my_obj), {"name": "John", "age": 42})

    def test_list(self):
        self.assertListEqual(jsonable.to([7, 8]), [7, 8])
        self.assertListEqual(jsonable.to(["hello", "world"]), ["hello", "world"])
        self.assertListEqual(jsonable.to([123, my_obj]), [123, {"name": "John", "age": 42}])

    def test_dict(self):
        self.assertDictEqual(jsonable.to({"one": 1, "two": 2}), {"one": 1, "two": 2})
        self.assertDictEqual(jsonable.to({"pers": my_obj}), {"pers": {"name": "John", "age": 42}})

