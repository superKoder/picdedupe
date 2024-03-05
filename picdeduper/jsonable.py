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
    def as_jsonable(self) -> Dict:
        pass


# # # # # # # # # # # # # # # # # # # 
#     Overloads of jsonable.to()    #
# # # # # # # # # # # # # # # # # # #
    
@singledispatch
def to(val):
    return val

@to.register
def _(val: int) -> int:
    return val

@to.register
def _(val: str) -> str:
    return val

@to.register
def _(val: float) -> float:
    return val

@to.register
def _(val: None) -> None:
    return val

@to.register
def _(val: list) -> List:
    return [to(x) for x in val]

@to.register
def _(val: dict) -> Dict:
    return {k: to(v) for (k,v) in val.items()}

@to.register
def _(val: Jsonable) -> Dict:
    return val.as_jsonable()

@to.register
def _(val: object) -> None:
    assert(False, "Derive from Jsonable and override .as_jsonable()")
    return None
