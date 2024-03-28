from enum import Enum


class OscDirection(Enum):
    Send = 1 << 0
    Receive = 1 << 1
    Bidirectional = 1 << 2
