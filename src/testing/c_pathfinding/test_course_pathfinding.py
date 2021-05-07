from unittest import TestCase
import logging
import cv2

from configparser import ConfigParser

from src.common.models.path import Path
from src.common.movement import climb
from src.c_pathfinding import course_pathfinding

logging.basicConfig(level=logging.DEBUG)


class TestCoursePathfinding(TestCase):
    def setUp(self):
        """
        Gets configuration
        """        
        conf_parser = ConfigParser()
        conf_parser.read("../../../resources/config.ini")
        self.conf = conf_parser["C_PATHFINDING"]

    def test_course_find_stair_center(self):
        snapshot = cv2.imread("../../../images/stair/pathfinding/06/img001.jpg")
        path: Path = course_pathfinding.run(conf=self.conf, snapshot=snapshot)
        assert path is not None