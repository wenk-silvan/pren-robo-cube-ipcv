from src.common.movement.direction import Direction
from src.common.movement.wheel_state import WheelState


class Drive:
    def __init__(self):
        self.wheels_front = WheelState.STRAIGHT
        self.wheels_back = WheelState.STRAIGHT

    def backward(self, distance):
        pass

    def forward(self, distance):
        pass

    def move(self, direction, value):
        if direction == Direction.DRIVE_BACK:
            self.backward(value)

        elif direction == Direction.DRIVE_FORWARD:
            self.forward(value)

        elif direction == Direction.ROTATE_BODY_RIGHT:
            self.rotate_body_right(value)

        elif direction == Direction.ROTATE_BODY_LEFT:
            self.rotate_body_left(value)

        elif direction == Direction.ROTATE_WHEELS_SIDEWAY:
            if self.wheels_front == WheelState.STRAIGHT and self.wheels_back == WheelState.STRAIGHT:
                self.rotate_all_wheels(angle=90)
            elif self.wheels_front == WheelState.STRAIGHT:
                self.rotate_front_wheels(angle=90)
            elif self.wheels_back == WheelState.STRAIGHT:
                self.rotate_back_wheels(angle=90)
            self.wheels_front, self.wheels_back = WheelState.SIDEWAYS

        elif direction == Direction.ROTATE_WHEELS_STRAIGHT:
            if self.wheels_front == WheelState.SIDEWAYS and self.wheels_back == WheelState.SIDEWAYS:
                self.rotate_all_wheels(angle=0)
            elif self.wheels_front == WheelState.SIDEWAYS:
                self.rotate_front_wheels(angle=0)
            elif self.wheels_back == WheelState.SIDEWAYS:
                self.rotate_back_wheels(angle=0)
            self.wheels_front, self.wheels_back = WheelState.STRAIGHT

    def rotate_body_left(self, angle):
        pass

    def rotate_body_right(self, angle):
        pass

    def rotate_front_wheels(self, angle):
        pass

    def rotate_back_wheels(self, angle):
        pass

    def rotate_all_wheels(self, angle):
        pass