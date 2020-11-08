import enum


class ColorTypes(enum.IntEnum):
    BLACK = 1
    COLORED = 4


class PrintModes(str, enum.Enum):
    SIMPLEX = "simplex"
    DUPLEX = "duplex"


class ShipTypes(str, enum.Enum):
    NATIONAL = "national"
    INTERNATIONAL = "international"


class JobStatus(str, enum.Enum):
    QUEUE = "queue"
    SENT = "sent"
    DELETED = "deleted"
    HOLD = "hold"
    TIMER = "timer"
