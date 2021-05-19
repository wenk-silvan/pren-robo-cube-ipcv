import logging
import time


class Climb:
    def __init__(self, serial_handler):
        self._serial_handler = serial_handler
        pass

    def head_up(self, duration):
        part = b'\x21'
        return self._climb(part, 1, duration)

    def head_down(self, duration):
        part = b'\x21'
        return self._climb(part, -1, duration)

    def body_up(self, duration):
        part = b'\x20'
        return self._climb(part, -1, duration)

    def body_down(self, duration):
        part = b'\x20'
        return self._climb(part, 1, duration)

    def tail_up(self, duration):
        part = b'\x22'
        return self._climb(part, 1, duration)

    def tail_down(self, duration):
        part = b'\x22'
        return self._climb(part, -1, duration)

    def _climb(self, part, direction, duration):
        """
        Triggers the Vertical mechanisms and lets the RoboCube lift or lower it's 3 Parts:
        :param part: x20 = body, x21 = head, x22 = tail
        :param direction: [-2, -1] = stop, [1, 2] = up
        :param duration: Time in seconds.
        :return:
        """
        logging.debug("Part: {} - Direction: {} - Duration {}".format(part, direction, duration))
        if direction not in [-2, -1, 1, 2]:
            logging.warning("%i does not count as valid direction!", direction)
            raise ValueError
        if duration > 256:
            logging.warning("%i ")
            raise ValueError

        # Send climbing command
        command = part + direction.to_bytes(1, byteorder='big', signed=True) + duration.to_bytes(1, byteorder='big',
                                                                                                 signed=False)
        self._serial_handler.send_command(command)

        polling = True
        while polling:
            status = self._serial_handler.check_status(b'\x28\x00\x00')
            if status[2] <= 0:
                polling = False
            time.sleep(0.05)

        return True
