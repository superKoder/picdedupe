from functools import singledispatch
from typing import Dict, List
# from abc import ABC, abstractmethod
import abc

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  The list of JSON-able types is very limited;
#    -  numbers (= int or float)
#    -  strings (= str)
#    -  null (= None)
#    -  arrays of any of the above (= list)
#    -  dictionaries of string to any of the above (= dict)
#
#  But good news! 
#
#  You can add to this list by implementing the Jsonable interface below!
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Jsonable(abc.ABC):
    """
    Interface for classes that can do their own conversions.
    """
    
    @abc.abstractmethod
    def jsonable_encode(self) -> Dict:
        """
        Turns an object into a json-able type, like a dict.
        """
        pass

    @abc.abstractclassmethod
    def jsonable_decode(jsonable):
        """
        Creates an object out of json-able type, like a dict.
        """
        pass


# # # # # # # # # # # # # # # # # # # 
#   Overloads of jsonable.encode()  #
# # # # # # # # # # # # # # # # # # #
    
@singledispatch
def encode(val):
    return val

@encode.register
def _(val: int) -> int:
    return val

@encode.register
def _(val: str) -> str:
    return val

@encode.register
def _(val: float) -> float:
    return val

@encode.register
def _(val: None) -> None:
    return val

@encode.register
def _(val: dict) -> Dict:
    return {k: encode(v) for (k,v) in val.items()}

@encode.register
def _(val: list) -> List:
    return [encode(x) for x in val]

@encode.register
def _(val: set) -> List:
    # sets are not jsonable, converting to list
    return sorted([encode(x) for x in val])

@encode.register
def _(val: Jsonable) -> Dict:
    return val.jsonable_encode()

@encode.register
def _(val: object) -> None:
    assert(False, "Derive from Jsonable and override .jsonable_encode()")
    return None


# # # # # # # # # # # # # # # # # # # 
#    Overloads of jsonable.from()   #
# # # # # # # # # # # # # # # # # # #

@singledispatch
def decode(as_type: type, val):
    return val

@decode.register
def _(val: int, as_type: type) -> int:
    return val

@decode.register
def _(val: str, as_type: type) -> str:
    return val

@decode.register
def _(val: float, as_type: type) -> float:
    return val

@decode.register
def _(val: None, as_type: type) -> None:
    return val

@decode.register
def _(val: dict, as_type: type):
    if hasattr(as_type, 'jsonable_decode'):
        return as_type.jsonable_decode(val)
    return val

@decode.register
def _(val: list, as_type: type):
    """
    `list` and `set` are special. The `as_type` is about the type of the elements!
    """
    if as_type == set:
        return set(decode(val, list))
    return [decode(x, as_type) for x in val]
