import logging
from unittest import TestCase

from src.common.communication.serial_handler import SerialHandler
from src.common.movement import sensors
from src.testing.common.communication import fake_serial
logging.basicConfig(filename='test.log', filemode='w', level=logging.DEBUG)


class TestSensor(TestCase):

    def setUp(self):
        """
        Creates fake serial connection
        """
        self.serial_object = fake_serial.Serial()
        self.serial_handler = SerialHandler(self.serial_object)
        self.sensor = sensors.Sensor(self.serial_handler)

    def test_left(self):
        assert self.sensor.left() in range(0, 10)  # 0-9

    def test_front_left(self):
        assert self.sensor.front_left() in range(0, 10)  # 0-9

    def test_front_right(self):
        assert self.sensor.front_right() in range(0, 10)  # 0-9

    def test_right(self):
        assert self.sensor.right() in range(0, 10)  # 0-9

    def test_down_front(self):
        assert self.sensor.down_front() in range(0, 10)  # 0-9

    def test_down_center(self):
        assert self.sensor.down_center() in range(0, 10)  # 0-9

    def test_down_tail(self):
        assert self.sensor.down_tail() in range(0, 10)  # 0-9

    def test__read_sensor(self):
        assert self.sensor._read_sensor(3) in range(0, 10)  # 0-9
