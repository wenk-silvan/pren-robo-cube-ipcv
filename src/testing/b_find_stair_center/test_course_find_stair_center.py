from unittest import TestCase
import logging

from src.b_find_stair_center.image_processing import ImageProcessing
from src.b_find_stair_center.stair_detection import StairDetection
from src.common.camera.fake_camera import FakeCamera
from src.common.communication.serial_handler import SerialHandler
from configparser import ConfigParser

from src.common.movement.drive import Drive
from src.common.object_detection import ObjectDetection
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

    def test_try_to_center(self):
        drive = Drive(self.serial_handler)
        pictogram_detection = ObjectDetection("../../../resources/cascades/pictogram/",
                                              ['hammer.xml', 'sandwich.xml', 'rule.xml', 'paint.xml', 'pencil.xml'])
        obstacle_detection = ObjectDetection("../../../resources/cascades/obstacle/", ["obstacle.xml"])
        stair_detection = StairDetection(self.conf, ImageProcessing(self.conf))
        is_centered = course_find_stair_center.try_to_center(self.conf, FakeCamera(), drive, pictogram_detection,
                                                             obstacle_detection, stair_detection)
