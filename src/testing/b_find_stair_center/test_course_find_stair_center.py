from unittest import TestCase
import logging

from src.common.camera.fake_camera import FakeCamera
from src.common.communication.serial_handler import SerialHandler
from configparser import ConfigParser
from src.testing.common.communication import fake_serial
from src.b_find_stair_center import course_find_stair_center

logging.basicConfig(level=logging.DEBUG)


class TestCourseFindStairCenter(TestCase):
    def setUp(self):
        """
        Creates fake serial connection and gets configuration
        """
        self.serial_object = fake_serial.Serial()
        self.serial_handler = SerialHandler(self.serial_object)

        conf_parser = ConfigParser()
        conf_parser.read("../../../resources/config.ini")
        self.conf = conf_parser["B_FIND_STAIR_CENTER"]

    def test_course_find_stair_center(self):
        snapshot = course_find_stair_center.run(conf=self.conf, serial=self.serial_handler, camera=FakeCamera())
        assert snapshot is not None
