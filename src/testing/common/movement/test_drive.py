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
        assert self.drive.forward(30) is True

    def test_forward_to_object(self):
        assert self.drive.forward_to_object(30) is True

    def test_left(self):
        assert self.drive.left(30) is True

    def test_move(self):
        for i in range(7):
            assert self.drive.move(3, 30) is True is True

    def test_right(self):
        assert self.drive.right(30) is True

    def test_rotate_body_left(self):
        assert self.drive.rotate_body_left(30) is True

    def test_rotate_body_right(self):
        assert self.drive.rotate_body_right(30) is True

    def test_stop(self):
        assert self.drive.stop() is True

    def test__rotate_front_wheels(self):
        assert self.drive._rotate_front_wheels(30) is True

    def test__rotate_back_wheels(self):
        assert self.drive._rotate_back_wheels(30) is True

    def test__rotate_all_wheels(self):
        assert self.drive._rotate_all_wheels(30) is True

    def test__drive(self):
        assert self.drive._drive(2, 12) is True

    def test__rotate_body(self):
        assert self.drive._rotate_body(2, 30) is True

    def test__polling_motors(self):
        assert self.drive._polling_motors() is True

    def test__rotate_wheels(self):
        assert self.drive._rotate_wheels(b'\x30', 90) is True
