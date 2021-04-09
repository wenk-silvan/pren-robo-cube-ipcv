import logging
import time

from src.movement.direction import Direction
from src.movement.wheel_state import WheelState


class Drive:
    def __init__(self, serial_handler):
        self._serial_handler = serial_handler
        self.wheels_front = WheelState.STRAIGHT
        self.wheels_back = WheelState.STRAIGHT

    def backward(self, distance):
        self.__drive(-2, distance)
        pass

    def forward(self, distance):
        self.__drive(2, distance)
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
        # TODO angle to distance try measure conclude
        self.__rotate_body(-1, angle)
        pass

    def rotate_body_right(self, angle):
        # TODO angle to distance
        self.__rotate_body(1, angle)
        pass

    def rotate_front_wheels(self, angle):
        servo = b'x30'
        self.__rotate_wheels(servo, angle)
        pass

    def rotate_back_wheels(self, angle):
        servo = b'x31'
        self.__rotate_wheels(servo, angle)
        pass

    def rotate_all_wheels(self, angle):
        servo = b'x32'
        self.__rotate_wheels(servo, angle)
        pass

    # All 4 Motors in the same direction/speed
    # direction: -2 backwards fast, -1 backwards ,1 forward, 2 forward fast
    # distance_cm: range 0 to 256
    def __drive(self, direction, distance_cm):
        if direction not in [-2, -1, 1, 2]:
            logging.warning("%i does not count as valid direction!", direction)
            pass
        if distance_cm > 256:
            logging.warning("%i ")
            pass

        # Actual driving
        command = b'x10' + direction.to_bytes(1, byteorder='big', signed=True) + distance_cm
        self._serial_handler.send_command(command)

        # Stay in Loop while still driving
        while self._serial_handler.check_status(b'\x19\x10\x00')[2] > 0.0:
            time.sleep(0.1)
            # TODO Pseudocode to functional code
            '''if (distance sensor reading < 100mm){
                set drive speed to 1
            }'''

    # All 4 Motors in 2 Groups (left/right)
    # direction: -2 left fast, -1 left, 1 right, 2 right fast
    # distance_cm: range 0 to 256
    def __rotate_body(self, direction, distance_cm):
        if direction not in [-2, -1, 1, 2]:
            logging.warning("%i does not count as valid direction!", direction)
            pass
        if distance_cm > 256:
            logging.warning("%i ")
            pass

        # Actual driving
        command = b'x15' + direction.to_bytes(1, byteorder='big', signed=True) + distance_cm
        self._serial_handler.send_command(command)

        # Stay in Loop while still driving
        while self._serial_handler.check_status(b'\x19\x15\x00')[2] > 0:
            time.sleep(0.1)
            # TODO Pseudocode to functional code
            '''if (distance sensor reading < 100mm){
                set drive speed to 1
            }'''

    # Front or back servo control
    # direction: -2 left fast, -1 left, 1 right, 2 right fast
    # distance_cm: range 0 to 256
    def __rotate_wheels(self, servo, angle):
        # Send rotation command
        command = servo + angle.to_bytes(1, byteorder='big', signed=True) + b'x00'
        self._serial_handler.send_command(command)
        time.sleep(0.5)  # Ensure there was enough time to turn the wheels (no check)
