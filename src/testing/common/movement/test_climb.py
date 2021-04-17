from unittest import TestCase
import logging

from src.common.communication.serial_handler import SerialHandler
from src.common.movement import climb
from src.testing.common.communication import fake_serial

logging.basicConfig(filename='test.log', filemode='w', level=logging.DEBUG)


class TestClimb(TestCase):

    def setUp(self):
        """
        Creates fake serial connection
        """
        self.serial_object = fake_serial.Serial()
        self.serial_handler = SerialHandler(self.serial_object)
        self.drive = climb.Climb(self.serial_handler)

    def test_head_up(self):
        assert self.drive.head_up(10) is True

    def test_head_down(self):
        assert self.drive.head_down(10) is True

    def test_body_up(self):
        assert self.drive.body_up(10) is True

    def test_body_down(self):
        assert self.drive.body_down(10) is True

    def test_tail_up(self):
        assert self.drive.tail_up(10) is True

    def test_tail_down(self):
        assert self.drive.tail_down(10) is True

    def test__climb(self):
        assert self.drive._climb(b'\x20', -1, 10) is True
