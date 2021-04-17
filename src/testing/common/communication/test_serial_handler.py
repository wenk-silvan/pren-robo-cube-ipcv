import logging
from unittest import TestCase
from src.common.communication.serial_handler import SerialHandler
from src.testing.common.communication import fake_serial
logging.basicConfig(filename='test.log', filemode='w', level=logging.INFO)


class TestSerialHandler(TestCase):

    def setUp(self):
        """
        Creates fake serial connection
        """
        self.serial_object = fake_serial.Serial()
        self.serial_handler = SerialHandler(self.serial_object)

    def test_send_command(self):
        answer = self.serial_handler.send_command(b'\x10\x01\x10')
        if (sum(answer[0:3]) % 256) == answer[3]:
            logging.debug(answer)

        assert answer[0:3].decode('utf-8').rstrip() == "ok!"

    def test_send_command_check_status(self):
        # send drive command
        answer = self.serial_handler.send_command(b'\x10\x01\x10')
        if (sum(answer[0:3]) % 256) == answer[3]:
            logging.debug(answer)

        # Check status until driving is over
        polling = True
        while polling:
            status = self.serial_handler.check_status(b'\x19\x00\x00')
            logging.debug("answer was: " + str(status))
            if status[2] <= 0:
                logging.debug("polling done!")
                polling = False
            logging.debug("polling.... ")
