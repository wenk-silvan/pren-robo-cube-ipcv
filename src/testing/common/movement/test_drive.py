import logging
from unittest import TestCase

from src.common.communication.serial_handler import SerialHandler
from src.common.movement import drive
from src.testing.common.communication import fake_serial

logging.basicConfig(filename='test.log', filemode='w', level=logging.DEBUG)


class TestDrive(TestCase):

    def setUp(self):
        """
        Creates fake serial connection
        """
        self.serial_object = fake_serial.Serial()
        self.serial_handler = SerialHandler(self.serial_object)
        self.drive = drive.Drive(self.serial_handler)

    def test_backward(self):
        assert self.drive.backward(30) is True

    def test_forward(self):
        self.fail()

    def test_forward_to_object(self):
        self.fail()

    def test_left(self):
        self.fail()

    def test_move(self):
        self.fail()

    def test_right(self):
        self.fail()

    def test_rotate_body_left(self):
        self.fail()

    def test_rotate_body_right(self):
        self.fail()

    def test_stop(self):
        self.fail()

    def test__rotate_front_wheels(self):
        self.fail()

    def test__rotate_back_wheels(self):
        self.fail()

    def test__rotate_all_wheels(self):
        self.fail()

    def test__drive(self):
        self.drive._drive(0, 12)

    def test__rotate_body(self):
        self.fail()

    def test__polling_motors(self):
        self.fail()

    def test__rotate_wheels(self):
        self.fail()
