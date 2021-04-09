from configparser import ConfigParser

from src.common.models.path import Path
from src.common.movement.direction import Direction
from src.common.movement.drive import Drive
from src.common.movement.drive_fake import DriveFake


def climb_stair(drive: Drive, path: Path):
    drive.forward_to_object()
    for instruction in path.instructions:
        drive.move(instruction.direction, instruction.distance)


def get_configuration():
    config_object = ConfigParser()
    config_object.read("../../resources/config.ini")
    return config_object["D_CLIMB_STAIR"]


def get_path():
    path = Path()
    path.add_instruction(Direction.DRIVE_LEFT, 20)
    path.add_instruction(Direction.DRIVE_RIGHT, 10)
    path.add_instruction(Direction.DRIVE_RIGHT, 0)
    path.add_instruction(Direction.DRIVE_LEFT, 50)
    path.add_instruction(Direction.DRIVE_LEFT, 0)
    path.add_instruction(Direction.DRIVE_RIGHT, 70)
    return path


def main():
    conf = get_configuration()
    # handler = SerialHandler()
    # drive = Drive(handler)
    drive = DriveFake()
    climb_stair(drive, get_path())


if __name__ == '__main__':
    main()
