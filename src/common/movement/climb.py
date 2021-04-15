import logging
import time


class Climb:
    def __init__(self, serial_handler):
        self._serial_handler = serial_handler
        pass

    def head_up(self, duration):
        part = b'x21'
        self._climb(part, 1, duration)
        pass

    def head_down(self, duration):
        part = b'x21'
        self._climb(part, -1, duration)
        pass

    def body_up(self, duration):
        part = b'20'
        self._climb(part, 1, duration)
        pass

    def body_down(self, duration):
        part = b'20'
        self._climb(part, -1, duration)
        pass

    def tail_up(self, duration):
        part = b'x22'
        self._climb(part, 1, duration)
        pass

    def tail_down(self, duration):
        part = b'x22'
        self._climb(part, -1, duration)
        pass

    def _climb(self, part, direction, duration):
        """
        Triggers the Vertical mechanisms and lets the RoboCube lift or lower it's 3 Parts:
        :param part: x20 = body, x21 = head, x22 = tail
        :param direction: [-2, -1] = down, [0] = stop, [1, 2] = up
        :param duration: Time in seconds.
        :return:
        """
        if direction not in [-2, -1, 0, 1, 2]:
            logging.warning("%i does not count as valid direction!", direction)
            pass
        if duration > 256:
            logging.warning("%i ")
            pass

        # Send climbing command
        command = part + direction.to_bytes(1, byteorder='big', signed=True) + duration
        self._serial_handler.send_command(command)

        # Stay in Loop while still climbing
        while self._serial_handler.check_status(b'\x28' + part + b'\x00')[2] > 0.0:
            time.sleep(0.1)
            # TODO Pseudocode to functional code
            '''if (distance sensor reading < 100mm){
                set drive speed to 1
            }'''