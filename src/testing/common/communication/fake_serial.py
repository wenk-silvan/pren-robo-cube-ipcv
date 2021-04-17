import logging
from random import randrange


class Serial:
    """
    Fake implementation of Serial connection which sends back some answers.
    """
    def __init__(self, port='COM1', baudrate=115200, timeout=1):
        self.name = port
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._isOpen = True
        self._receivedData = ""
        self.last_data = None
        self.counter = 0
        self.status_reading = False
        self.reading_first_byte = None

    def read(self, n) -> bytes:
        if n != 4:
            raise ValueError
        if self.reading_first_byte in (b'\x19', b'\x28', b'\x29'):
            logging.debug("case [\\x19 \\x28' \\x29]")
            data = self.reading_first_byte + b'\x00' + self.counter.to_bytes(1, byteorder='big', signed=False)
            return data + (sum(data) % 256).to_bytes(1, byteorder='big', signed=False)

        if self.reading_first_byte == b'\x40':
            logging.debug("case [\\x40]")
            data = self.reading_first_byte + b'\x00' + randrange(10).to_bytes(1, byteorder='big', signed=False)
            return data + (sum(data) % 256).to_bytes(1, byteorder='big', signed=False)

        else:
            return bytes("ok!", 'utf-8') + b'\xfb'

    def write(self, data):
        logging.debug("FAKE: write - got data" + str(data))
        if data[0].to_bytes(1, byteorder='big', signed=False) not in (b'\x19', b'\x28', b'\x29', b'\x40'):
            self.status_reading = True
            self.counter = 21
            self.last_data = data
        else:
            self.reading_first_byte = data[0].to_bytes(1, byteorder='big', signed=False)
            self.status_reading = False
            self.counter -= 1
        logging.debug("write was called... counter at {}, last data: {}".format(self.counter, self.last_data))
        pass

    def flush(self):
        pass
