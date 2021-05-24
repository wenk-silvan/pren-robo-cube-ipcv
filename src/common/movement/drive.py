import logging
import time

from src.common.movement.direction import Direction
from src.common.movement.sensors import Sensor
from src.common.movement.wheel_state import WheelState
from src.common.movement.climb import Climb


class Drive:
    def __init__(self, serial_handler):
        self._serial_handler = serial_handler
        self._sensors = Sensor(self._serial_handler)
        self._climb = Climb(self._serial_handler)
        self._climb.tail_up_slow(40)
        self._climb.head_down_slow(50)
        self._climb.tail_down_fast(9)
        self._climb.head_up_fast(5)
        self.wheels_orientation = WheelState.STRAIGHT
        self._rotate_all_wheels(1)

    def backward(self, distance):
        """
        Triggers the robot to drive backward by first rotating all wheels to 0 degrees and then driving backward.
        :param distance: The distance in millimeters.
        """
        logging.info("Drive: backward %s cm", distance)
        if self.wheels_orientation != WheelState.STRAIGHT:
            self._rotate_all_wheels(0)
            self.wheels_orientation = WheelState.STRAIGHT
        return self._drive_distance(-2, distance)

    def backward_slow(self, distance):
        """
        Triggers the robot to drive backward by first rotating all wheels to 0 degrees and then driving backward.
        :param distance: The distance in millimeters.
        """
        logging.info("Drive: backward %s cm", distance)
        if self.wheels_orientation != WheelState.STRAIGHT:
            self._rotate_all_wheels(0)
            self.wheels_orientation = WheelState.STRAIGHT
        return self._drive_distance(-1, distance)

    def forward(self, distance):
        """
        Triggers the robot to drive forward by first rotating all wheels to 0 degrees and then driving forward.
        :param distance: The distance in millimeters.
        """
        logging.info("Drive: forward %s cm", distance)
        if self.wheels_orientation != WheelState.STRAIGHT:
            self._rotate_all_wheels(0)
            self.wheels_orientation = WheelState.STRAIGHT
        return self._drive_distance(2, distance)
        pass

    def forward_slow(self, distance):
        """
        Triggers the robot to drive forward by first rotating all wheels to 0 degrees and then driving forward.
        :param distance: The distance in millimeters.
        """
        logging.info("Drive: forward %s cm", distance)
        if self.wheels_orientation != WheelState.STRAIGHT:
            self._rotate_all_wheels(0)
            self.wheels_orientation = WheelState.STRAIGHT
        return self._drive_distance(1, distance)
        pass

    def forward_to_object(self, threshold):
        """
        Triggers the robot to drive forward until the sensor sends a stop signal, objects will be closer to camera.
        :param threshold: The threshold in mm to approach object
        """
        logging.info("Drive: forward to object until %s mm away", threshold)
        if self.wheels_orientation != WheelState.STRAIGHT:
            self._rotate_all_wheels(0)
            self.wheels_orientation = WheelState.STRAIGHT
        return self._drive_sensors(1, threshold)

    def left(self, distance):
        """
        Triggers the robot to drive to the left by first rotating all wheels to 90 degrees and then driving backward.
        :param distance: The distance in millimeters.
        """
        logging.info("Drive: left %s mm", distance)
        if self.wheels_orientation != WheelState.SIDEWAYS:
            self._rotate_all_wheels(90)
            self.wheels_orientation = WheelState.SIDEWAYS
        return self._drive_distance(-2, distance)

    def move(self, direction, value):
        """
        Triggers to move the robot by the given value and direction.
        :param direction:
        :param value: Either distance in millimeters or angle in degrees
        :return:
        """
        if direction == Direction.DRIVE_BACK.value:
            return self.backward(value)
        elif direction == Direction.DRIVE_FORWARD.value:
            return self.forward(value)
        elif direction == Direction.DRIVE_LEFT.value:
            return self.left(value)
        elif direction == Direction.DRIVE_RIGHT.value:
            return self.right(value)
        elif direction == Direction.ROTATE_BODY_RIGHT.value:
            return self.rotate_body_right(value)
        elif direction == Direction.ROTATE_BODY_LEFT.value:
            return self.rotate_body_left(value)

    def right(self, distance):
        """
        Triggers the robot to drive to the right by first rotating all wheels to 90 degrees and then driving forward.
        :param distance: The distance in millimeters.
        """
        logging.info("Drive: right %s mm", distance)
        if self.wheels_orientation != WheelState.SIDEWAYS:
            self._rotate_all_wheels(90)
            self.wheels_orientation = WheelState.SIDEWAYS
        return self._drive_distance(2, distance)

    def rotate_body_left(self, angle):
        """
        Triggers the robot to rotate to the left, around his own axis.
        :param angle: The angle in degrees.
        """
        logging.info("Rotate: body left %s to degree", angle)
        return self._rotate_body(-1, angle)

    def rotate_body_right(self, angle):
        """
        Triggers the robot to rotate to the right, around his own axis.
        :param angle: The angle in degrees.
        """
        logging.info("Rotate: body right %s to degree", angle)
        return self._rotate_body(1, angle)

    def stop(self):
        logging.info("Drive: Stop driving now")
        return self._drive_distance(1, 0)

    def _rotate_all_wheels(self, angle):
        servo = b'\x30'
        logging.debug("Rotate all wheels to %s degree", angle)
        return self._rotate_wheels(servo, angle)

    def _rotate_front_wheels(self, angle):
        servo = b'\x31'
        logging.debug("Rotate front wheels to %s degree", angle)
        return self._rotate_wheels(servo, angle)

    def _rotate_back_wheels(self, angle):
        servo = b'\x32'
        logging.debug("Rotate back wheels to %s degree", angle)
        return self._rotate_wheels(servo, angle)

    def _rotate_wheels_diagonal(self):
        # Something  /  \
        #  like so   \  /
        servo = b'\x33'
        self.wheels_orientation = WheelState.DIAGONAL
        logging.debug("Rotate wheels in diagonal direction to 45 degree to rotate body.")
        return self._rotate_wheels(servo, 45)

    def _rotate_wheels(self, servo, angle):
        """
        Actual Rotation of the Wheels. Triggers one or two servos.
        Wheels need to be in the air in order to turn them.
        :param servo: x30 = front, x31 = back, x32 = both
        :param angle: [-45 to 90] the Angle the Servos should turn.
        :return:
        """
        self._climb.body_down_fast(8)
        command = servo + angle.to_bytes(1, byteorder='big', signed=True) + b'\x00'
        self._serial_handler.send_command(command)
        time.sleep(0.5)  # Ensure there was enough time to turn the wheels (no check)
        self._climb.body_up_fast(8)
        return True

    def _drive_distance(self, direction, distance_cm):
        self._drive(direction, distance_cm)
        return self._polling_motors()

    def _drive_sensors(self, direction, threshold):
        self._drive(direction, 200)
        return self._polling_sensors(threshold)

    def _drive(self, direction, distance_cm):
        """
        Actual Driving. Triggers the 4 Motors (all in the same direction)
        :param direction: [-2, -1] = backward, [1, 2] = forward
        :param distance_cm: [0 to 256] The distance in cm the robot should drive
        :return:
        """
        if direction not in [-2, -1, 1, 2]:
            logging.warning("%i does not count as valid direction!", direction)
            raise ValueError
        if distance_cm > 256:
            logging.warning("%i ")
            raise ValueError

        logging.debug("Drive direction: %s for %s mm", direction, distance_cm)
        # Actual driving
        command = b'\x10' + direction.to_bytes(1, byteorder='big', signed=True)\
                  + distance_cm.to_bytes(1, byteorder='big', signed=False)
        self._serial_handler.send_command(command)

    def _rotate_body(self, direction, distance_cm):
        """
        Actual Turning. Triggers the 4 Motors (left/right in opposite direction)
        :param direction: [-2, -1] = turn left, [1, 2] = turn right
        :param distance_cm: [0 to 256] The "distance" for the motors to travel.
        # TODO This needs to be tested and tuned with the whole body attached!
        :return:
        """
        if direction not in [-2, -1, 1, 2]:
            logging.warning("%i does not count as valid direction!", direction)
            raise ValueError
        if distance_cm > 256:
            logging.warning("%i ")
            raise ValueError

        if not self.wheels_orientation == WheelState.DIAGONAL:
            self._rotate_wheels_diagonal()

        # TODO what command to use / Check with Michael
        command = b'\x15' + direction.to_bytes(1, byteorder='big', signed=True) \
                  + distance_cm.to_bytes(1, byteorder='big', signed=False)
        self._serial_handler.send_command(command)

        return True

    def _polling_motors(self):
        """
        Used to verify if the 4 main Motors are still running.
        :return: True once the motors have stopped
        """
        polling = True
        while polling:
            status = self._serial_handler.check_status(b'\x19\x00\x00')
            if status[2] <= 0:
                polling = False
            time.sleep(0.05)

        return True

    def _polling_sensors(self, threshold):
        """
        Used to check the distance in a given direction
        :return: True once the motors have stopped
        """
        distances = []
        polling = True
        while polling:
            distances.append(self._sensors.front_right())
            distances.append(self._sensors.front_left())
            if min(distances) <= threshold:
                polling = False
            time.sleep(0.005)

        return True
