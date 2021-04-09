import cv2
import time
from configparser import ConfigParser

from src.b_find_stair_center.image_processing import ImageProcessing
from src.common.communication.serial_handler import SerialHandler
from src.common.object_detection import ObjectDetection
from src.b_find_stair_center.stair_detection import StairDetection
from src.common.movement.drive_fake import DriveFake


def get_configuration():
    config_object = ConfigParser()
    config_object.read("../../resources/config.ini")
    return config_object["B_FIND_STAIR_CENTER"]


def main():
    conf = get_configuration()
    # handler = SerialHandler()
    # drive = Drive(handler)
    # camera = Camera()
    drive = DriveFake()

    pictogram_detection = ObjectDetection("../../resources/cascades/pictogram/",
                                          ['hammer.xml', 'sandwich.xml', 'rule.xml', 'paint.xml', 'pencil.xml'])
    obstacle_detection = ObjectDetection("../../resources/cascades/obstacle/", ["obstacle.xml"])
    stair = StairDetection(conf, ImageProcessing(conf))
    is_centered = False

    while not is_centered:
        # image = camera.snapshot()
        image = cv2.resize(cv2.imread(conf["img_2_path"]), (1280, 960))

        pictograms = pictogram_detection.detect(image, 1000, 15000, float(conf["detection_pictogram_scale"]),
                                                int(conf["detection_pictogram_neighbours"]))
        obstacles = obstacle_detection.detect(image, 2000, 30000, float(conf["detection_obstacle_scale"]),
                                              int(conf["detection_obstacle_neighbours"]))

        lines_vertical, lines_horizontal = stair.detect_lines(image)
        direction, value, is_centered = stair.get_next_movement(
            image, lines_vertical, lines_horizontal, pictograms, len(obstacles) > 0)

        print("Next move: {} with a distance of {}".format(direction, value))
        drive.move(direction, value)
        time.sleep(2)


if __name__ == '__main__':
    main()
