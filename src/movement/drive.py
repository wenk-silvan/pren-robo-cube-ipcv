import logging
from src.movement.direction import Direction

class Drive:
    def __init__(self, conf, conn):
        # TODO: Initialize connection to drive controller
        self.conf = conf
        pass

    def backwards(self, distance):
        pass

    def forward(self, distance):
        pass

    def is_moving(self):
        pass

    def rotate_left(self, angle):
        pass

    def rotate_right(self, angle):
        pass

    def move(self, direction, value):
        if not isinstance(direction, Direction):
            logging.error("The provided object is not of type Direction.")
            return

        if direction == Direction.ROTATE_LEFT:
            self.rotate_left(value)
        elif direction == Direction.ROTATE_RIGHT:
            self.rotate_right(value)
        elif direction == Direction.DRIVE_BACK:
            self.backwards(value)
        elif direction == Direction.DRIVE_FORWARD:
            self.forward(value)

