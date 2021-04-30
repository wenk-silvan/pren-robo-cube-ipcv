from src.common.communication.serial_handler import SerialHandler
from src.common.movement.drive import Drive
from src.common.movement.climb import Climb
from configparser import ConfigParser


def drive_floor(conf, drive: Drive):
    drive.forward(50)
    drive.left(50)
    drive.backward(50)
    drive.right(50)


def climb_step(conf, drive: Drive, climb: Climb):
    duration = conf["climb_step_duration"]
    climb.head_up(duration)
    drive.forward(conf["climb_forward_head_mm"])
    climb.body_up(duration)
    drive.forward(conf["climb_forward_body_mm"])
    climb.tail_up(duration)
    drive.forward(conf["climb_forward_tail_mm"])


def main():
    conf_parser = ConfigParser()
    conf_parser.read("resources/config.ini")
    conf = conf_parser["D_CLIMB_STAIR"]

    serial_handler = SerialHandler()
    drive = Drive(serial_handler)
    climb = Climb(serial_handler)
    drive_floor(conf, drive)
    climb_step(conf, drive, climb)


if __name__ == '__main__':
    main()
