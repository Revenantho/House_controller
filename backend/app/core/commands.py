from enum import Enum


class Command(str, Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    STOP = "STOP"
    SET_POSITION = "SET_POSITION"


class DeviceType(str, Enum):
    ROLLER_SHUTTER = "ROLLER_SHUTTER"
    GARAGE_DOOR = "GARAGE_DOOR"
