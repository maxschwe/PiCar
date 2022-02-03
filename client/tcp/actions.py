from enum import Enum

# possible ACTION
# Max types is 2^8=256 (One Byte)


class ACTIONS(Enum):
    PING = 0
    ACK = 1
    DISCONNECT = 2
    HI = 3
    ECHO = 4
    PUT = 5
    RESTART = 6
    ERROR = 7
    SPEED = 8
    STEERING = 9
    LIVESTREAM = 10
    LOAD_STATUS = 11

    @classmethod
    def decode(cls, code):
        return cls(code)

    @classmethod
    def list(cls):
        return list(map(lambda c: c, cls))
