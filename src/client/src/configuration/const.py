from enum import Enum

# possible ACTION
# Max types is 2^8=256 (One Byte)


class ACTION(Enum):
    PING = 0
    ACK = 1
    DISCONNECT = 2
    HI = 3
    ECHO = 4
    PUT = 5
    RESTART = 6
    STRAIGHT = 7
    TURN = 8
    BACKWARD = 9
    SPEED = 10
    STEERING = 11

    @classmethod
    def decode(cls, code):
        return cls(code)

    @classmethod
    def list(cls):
        return list(map(lambda c: c, cls))

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

    @classmethod
    def list(cls):
        return list(map(lambda c: c, cls))
