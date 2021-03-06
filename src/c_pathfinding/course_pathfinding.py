import cv2
from configparser import ConfigParser

import numpy as np

from src.b_find_stair_center.image_processing import ImageProcessing
from src.c_pathfinding.pathfinder import Pathfinder
from src.common.image_manipulator import ImageManipulator
from src.common.models.obstacle import Obstacle
from src.common.object_detection import ObjectDetection
import logging


def run(conf, snapshot):
    try:
        # TODO: Adjust detection parameters
        detection = ObjectDetection("", [])
        obstacles = detection.detect_obstacles(snapshot)
        
        manipulator = ImageManipulator(snapshot)
        image, transform_matrix = manipulator.transform_to_2d((600, 600))
        obstacles = [manipulator.transform_obstacle_coordinates(transform_matrix, o) for o in obstacles]

        finder = Pathfinder(image, conf)
        stair_with_objects = finder.create_stair_with_objects(obstacles)
        if stair_with_objects.count() < 6:
            raise RuntimeError("Less than 6 steps where detected.")
        stair_with_areas = finder.create_stair_passable_areas(stair_with_objects)
        paths = finder.calculate_path(stair_with_areas)
        path = Pathfinder.determine_best_path(paths)

        # detector.draw_objects(image, obstacles, (0, 0, 255))
        # cv2.imshow("Result", image)
        # cv2.waitKey(0)

        message = "====== All paths: ======\n"
        for p in paths:
            message += p.to_string()
        logging.info(message)

        logging.info("====== Fastest path: ======\n%s", path.to_string())
        return path
    except RuntimeError as e:
        logging.error("Error in c_pathfinding:\n%s", e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    conf_parser = ConfigParser()
    conf_parser.read("resources/config.ini")
    conf = conf_parser["C_PATHFINDING"]
    image_raw = cv2.imread(conf["img_3_path"])
    run(conf=conf, snapshot=image_raw)
