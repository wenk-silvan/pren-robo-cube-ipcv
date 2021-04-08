import logging
import time


class Climb:
    def __init__(self, serial_handler):
        self._serial_handler = serial_handler
        pass

    def head_up(self, duration):
        part = b'x20'
        self.__climb(part, 1, duration)
        pass

    def head_down(self, duration):
        part = b'x20'
        self.__climb(part, -1, duration)
        pass

    def body_up(self, duration):
        part = b'x21'
        self.__climb(part, 1, duration)
        pass

    def body_down(self, duration):
        part = b'x21'
        self.__climb(part, -1, duration)
        pass

    def tail_up(self, duration):
        part = b'x22'
        self.__climb(part, 1, duration)
        pass

    def tail_down(self, duration):
        part = b'x22'
        self.__climb(part, -1, duration)
        pass

    # All 4 Motors in the same direction/speed
    # direction: -2 backwards fast, -1 backwards ,1 forward, 2 forward fast
    # distance_cm: range 0 to 256
    def __climb(self, part, direction, duration):
        if direction not in [-2, -1, 1, 2]:
            logging.warning("%i does not count as valid direction!", direction)
            pass
        if duration > 256:
            logging.warning("%i ")
            pass

        # Send climbing command
        command = part + direction.to_bytes(1, byteorder='big', signed=True) + duration
        self._serial_handler.send_command(command)

        # Stay in Loop while still driving
        while self._serial_handler.check_status(b'\x28' + part + b'\x00')[2] > 0.0:
            time.sleep(0.1)
            # TODO Pseudocode to functional code
            '''if (distance sensor reading < 100mm){
                set drive speed to 1
            }'''