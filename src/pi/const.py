from enum import Enum

# possible Actions


class ACTIONS(Enum):
    PING = 0
    ACK = 1
    DISCONNECT = 2

    @classmethod
    def decode(cls, code):
        return cls(code)

# possible Return Types


class RETURN(Enum):
    DICT = 0
    TEXT = 1
    INT = 2
    FLOAT = 3
    BOOL = 4
    LIST = 5
    ACK = 6
    NONE = 7

    @classmethod
    def decode(cls, code):
        return cls(code)
