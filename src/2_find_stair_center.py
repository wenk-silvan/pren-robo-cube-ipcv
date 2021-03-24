from drive import Drive
from stair_detection import StairDetection
from configparser import ConfigParser


def get_configuration(path):
    config_object = ConfigParser()
    config_object.read(path)
    return config_object["CONFIGURATION"]


def main():
    conf = get_configuration("../config.ini")
    drive = Drive()
    stair_detection = StairDetection(conf)

    while not stair_detection.detect_stair():
        # TODO: Wait for robot to have turned
        drive.rotate_left(int(conf["drive_rotation_angle"]))


main()
exit(0)
