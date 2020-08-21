from enum import Enum



class Types(Enum):
    TEXT = 0
    INTEGER = 1
    NUMBER = 2
    BOOLEAN = 3

TYPES = {
    "text": Types.TEXT,
    "int": Types.INTEGER,
    "num": Types.NUMBER,
    "bool": Types.BOOLEAN
}