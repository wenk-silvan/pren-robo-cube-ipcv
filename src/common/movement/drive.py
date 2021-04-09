import logging
import time

from src.common.movement.direction import Direction
from src.common.movement.wheel_state import WheelState


class Drive:
    def __init__(self, serial_handler):
        self._serial_handler = serial_handler
        self.wheels_orientation = WheelState.STRAIGHT

    def backward(self, distance):
        """
        Triggers the robot to drive backward by first rotating all wheels to 0 degrees and then driving backward.
        :param distance: The distance in millimeters.
        """
        if self.wheels_orientation == WheelState.SIDEWAYS:
            self._rotate_all_wheels(0)
            self.wheels_orientation = WheelState.STRAIGHT
        self._drive(-2, distance)
        pass

    def forward(self, distance):
        """
        Triggers the robot to drive forward by first rotating all wheels to 0 degrees and then driving forward.
        :param distance: The distance in millimeters.
        """
        if self.wheels_orientation == WheelState.SIDEWAYS:
            self._rotate_all_wheels(0)
            self.wheels_orientation = WheelState.STRAIGHT
        self._drive(2, distance)
        pass

    def forward_to_object(self):
        """
        Triggers the robot to drive forward until the sensor sends a stop signal, objects will be closer to camera.
        """
        if self.wheels_orientation == WheelState.SIDEWAYS:
            self._rotate_all_wheels(0)
        # TODO: Drive until sensor hits.

    def left(self, distance):
        """
        Triggers the robot to drive to the left by first rotating all wheels to 90 degrees and then driving backward.
        :param distance: The distance in millimeters.
        """
        if self.wheels_orientation == WheelState.STRAIGHT:
            self._rotate_all_wheels(90)
            self.wheels_orientation = WheelState.SIDEWAYS
        self._drive(-2, distance)

    def move(self, direction, value):
        """
        Triggers to move the robot by the given value and direction.
        :param direction:
        :param value: Either distance in millimeters or angle in degrees
        :return:
        """
        if direction == Direction.DRIVE_BACK:
            self.backward(value)
        elif direction == Direction.DRIVE_FORWARD:
            self.forward(value)
        elif direction == Direction.DRIVE_LEFT:
            self.left(value)
        elif direction == Direction.DRIVE_RIGHT:
            self.right(value)
        elif direction == Direction.ROTATE_BODY_RIGHT:
            self.rotate_body_right(value)
        elif direction == Direction.ROTATE_BODY_LEFT:
            self.rotate_body_left(value)

    def right(self, distance):
        """
        Triggers the robot to drive to the right by first rotating all wheels to 90 degrees and then driving forward.
        :param distance: The distance in millimeters.
        """
        if self.wheels_orientation == WheelState.STRAIGHT:
            self._rotate_all_wheels(90)
            self.wheels_orientation = WheelState.SIDEWAYS
        self._drive(2, distance)

    def rotate_body_left(self, angle):
        """
        Triggers the robot to rotate to the left, around his own axis.
        :param angle: The angle in degrees.
        """
        # TODO angle to distance try measure conclude
        self._rotate_body(-1, angle)
        pass

    def rotate_body_right(self, angle):
        """
        Triggers the robot to rotate to the right, around his own axis.
        :param angle: The angle in degrees.
        """
        # TODO angle to distance
        self._rotate_body(1, angle)
        pass

    def _rotate_front_wheels(self, angle):
        servo = b'\x30'
        self._rotate_wheels(servo, angle)
        pass

    def _rotate_back_wheels(self, angle):
        servo = b'\x31'
        self._rotate_wheels(servo, angle)
        pass

    def _rotate_all_wheels(self, angle):
        servo = b'\x32'
        self._rotate_wheels(servo, angle)
        pass

    # All 4 Motors in the same direction/speed
    # direction: -2 backwards fast, -1 backwards ,1 forward, 2 forward fast
    # distance_cm: range 0 to 256
    def _drive(self, direction, distance_cm):
        if direction not in [-2, -1, 1, 2]:
            logging.warning("%i does not count as valid direction!", direction)
            pass
        if distance_cm > 256:
            logging.warning("%i ")
            pass

        # Actual driving
        command = b'\x10' + direction.to_bytes(1, byteorder='big', signed=True) + distance_cm
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
    def _rotate_body(self, direction, distance_cm):
        if direction not in [-2, -1, 1, 2]:
            logging.warning("%i does not count as valid direction!", direction)
            pass
        if distance_cm > 256:
            logging.warning("%i ")
            pass

        # Actual driving
        command = b'\x15' + direction.to_bytes(1, byteorder='big', signed=True) + distance_cm
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
    def _rotate_wheels(self, servo, angle):
        # Send rotation command
        command = servo + angle.to_bytes(1, byteorder='big', signed=True) + b'x00'
        self._serial_handler.send_command(command)
        time.sleep(0.5)  # Ensure there was enough time to turn the wheels (no check)
