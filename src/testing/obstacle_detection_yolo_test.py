from configparser import ConfigParser

import cv2
from src.common.obstacle_detection_yolo import ObstacleDetectionYolo

from src.common.image_manipulator import ImageManipulator


def _pass(_):
    pass


if __name__ == '__main__':
    conf_parser = ConfigParser()
    conf_parser.read("../../resources/config.ini")
    conf = conf_parser["C_PATHFINDING"]

    image = cv2.imread("../../images/stair/pathfinding/outdoor.jpg")
    detection = ObstacleDetectionYolo(conf)
    obstacles = detection.detect(image)
    detection.draw(image, obstacles, (255, 255, 0))
    # image_manipulator = ImageManipulator(image)
    # image = image_manipulator.transform_to_2d((600, 600))
    # blurred = cv2.GaussianBlur(img, (5, 5), 0, 0)
    # gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    cv2.imshow('dst', image)
    cv2.waitKey(0)
