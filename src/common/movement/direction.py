from enum import Enum


class Direction(Enum):
    DRIVE_FORWARD = 1
    DRIVE_BACK = 2
    ROTATE_BODY_LEFT = 3
    ROTATE_BODY_RIGHT = 4
    ROTATE_WHEELS_SIDEWAYS = 5
    ROTATE_WHEELS_STRAIGHT = 6
