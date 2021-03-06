import time
from configparser import ConfigParser
import logging

from src.common.camera.camera import Camera
from src.common.communication.serial_handler import SerialHandler
from src.b_find_stair_center.image_processing import ImageProcessing
from src.common.movement.drive import Drive
from src.common.object_detection import ObjectDetection
from src.b_find_stair_center.stair_detection import StairDetection


def run(conf, camera: Camera, drive: Drive):
    try:
        object_detection = ObjectDetection("resources/cascades/pictogram/",
                                              ['hammer.xml', 'sandwich.xml', 'rule.xml', 'paint.xml', 'pencil.xml'])
        stair_detection = StairDetection(conf, ImageProcessing(conf))
        is_centered = False

        while not is_centered:
            is_centered = try_to_center(conf, camera, drive, object_detection, stair_detection)
            time.sleep(2)
        logging.info("Robot is centered, take snapshot.")
        return camera.snapshot()
    except RuntimeError as e:
        logging.error("Error in b_find_stair_center:\n", e)


def try_to_center(conf, camera, drive, object_detection, stair_detection):
    image = camera.snapshot()
    pictograms = []
    for i in range(2):
        if len(pictograms) > 0:
            break
        pictograms = object_detection.detect_pictograms(image, int(conf["detection_pictogram_min_area"]),
                                                        int(conf["detection_pictogram_max_area"]),
                                                        float(conf["detection_pictogram_scale"]),
                                                        int(conf["detection_pictogram_neighbours"]))
    # obstacles = object_detection.detect_obstacles(image)
    obstacles = []

    lines_vertical, lines_horizontal = stair_detection.detect_lines(image)

    # UNCOMMENT FOR TESTING
    # pictogram_detection.draw_objects(image, pictograms, (0, 255, 0))
    # obstacle_detection.draw_objects(image, obstacles, (0, 0, 255))
    # ImageProcessing.draw_lines(lines_vertical, image)
    # ImageProcessing.draw_lines(lines_horizontal, image)
    # cv2.imshow("Result", image)
    # cv2.waitKey(0)

    direction, value, done = stair_detection.get_next_movement(
        image, lines_vertical, lines_horizontal, pictograms, len(obstacles) > 0)

    logging.info("Try to center robot, detected pictograms: %s, obstacles: %s, vert_lines: %s, hor_lines: %s\n"
                 "Next move is %s with a distance of %s mm.",
                 len(pictograms), len(obstacles), len(lines_vertical), len(lines_horizontal), direction, value)

    drive.move(direction, value)
    return done


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    conf_parser = ConfigParser()
    conf_parser.read("resources/config.ini")
    serial = SerialHandler()
    run(conf=conf_parser["B_FIND_STAIR_CENTER"], camera=Camera(), drive=Drive(serial))
