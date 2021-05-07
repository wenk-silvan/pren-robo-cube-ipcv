from unittest import TestCase
import logging

from configparser import ConfigParser
from src.common.communication.serial_handler import SerialHandler
from src.testing.common.communication import fake_serial
from src.common.models.path import Path
from src.common.movement.direction import Direction
from src.e_find_pictogram import course_find_pictogram

logging.basicConfig(level=logging.DEBUG)


class TestCourseFindPictogram(TestCase):
    def setUp(self):
        """
        Creates fake serial connection and gets configuration
        """
        self.serial_object = fake_serial.Serial()
        self.serial_handler = SerialHandler(self.serial_object)

        conf_parser = ConfigParser()
        conf_parser.read("../../../resources/config.ini")
        self.conf = conf_parser["D_CLIMB_STAIR"]

    def test_course_find_stair_center(self):
        pictogram = "hammer"
        path = Path()
        path.add_instruction(Direction.DRIVE_LEFT, 20)
        path.add_instruction(Direction.DRIVE_RIGHT, 10)
        path.add_instruction(Direction.DRIVE_RIGHT, 0)
        path.add_instruction(Direction.DRIVE_LEFT, 50)
        path.add_instruction(Direction.DRIVE_LEFT, 0)
        path.add_instruction(Direction.DRIVE_RIGHT, 70)

        final_position = path.get_final_position()
        success = course_find_pictogram.run(
            pictogram=pictogram,
            position_robot=final_position,
            serial=self.serial_handler)

        assert final_position is 60
        assert success is True
