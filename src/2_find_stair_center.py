import time, cv2
from src.movement.drive import Drive
from src.stair.stair_detection import StairDetection
from configparser import ConfigParser
from src.camera.camera import Camera
from src.movement.direction import Direction


def get_configuration(path):
    config_object = ConfigParser()
    config_object.read(path)
    return config_object["CONFIGURATION"]


def main():
    conf = get_configuration("../config.ini")
    drive = Drive(conf, None)
    camera = Camera(conf)
    stair_detection = StairDetection(conf)

    while not stair_detection.is_centered():
        # image = camera.snapshot()
        image = cv2.imread(conf["img_path"])
        image = cv2.resize(image, (1280, 960))
        detected = stair_detection.detect_first_step(image)
        if detected is None:
            drive.move(Direction.ROTATE_RIGHT, int(conf["drive_rotation_angle"]))
        else:
            direction, value = stair_detection.get_next_movement(detected, image)
            drive.move(direction, value)
        while drive.is_moving():
            time.sleep(0.5)


main()
exit(0)
