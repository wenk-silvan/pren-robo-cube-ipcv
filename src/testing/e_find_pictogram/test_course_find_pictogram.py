from unittest import TestCase
import logging

from configparser import ConfigParser
from src.common.communication.serial_handler import SerialHandler
from src.common.models.instruction import Instruction
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
        self.conf = conf_parser["E_FIND_PICTOGRAM"]

    def test_run(self):
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
            conf=self.conf,
            pictogram=pictogram,
            position_robot=final_position,
            serial=self.serial_handler)

        assert final_position == 60
        assert success is True

    def test_get_instruction_right(self):
        expected: Instruction = Instruction(Direction.DRIVE_RIGHT, 130)
        actual: Instruction = course_find_pictogram.get_instruction(position_pictogram=180, position_robot=50)
        assert expected.direction == actual.direction
        assert expected.distance == actual.distance

    def test_get_instruction_left(self):
        expected: Instruction = Instruction(Direction.DRIVE_LEFT, 420)
        actual: Instruction = course_find_pictogram.get_instruction(position_pictogram=180, position_robot=600)
        assert expected.direction == actual.direction
        assert expected.distance == actual.distance

    def test_get_position_pictogram_hammer(self):
        assert course_find_pictogram.get_position_pictogram(self.conf, "hammer") == 180

    def test_get_position_pictogram_distance_between(self):
        position_hammer = course_find_pictogram.get_position_pictogram(self.conf, "hammer")
        position_sandwich = course_find_pictogram.get_position_pictogram(self.conf, "sandwich")
        assert position_sandwich - position_hammer == 250
