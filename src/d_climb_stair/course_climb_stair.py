from configparser import ConfigParser

from src.common.communication.serial_handler import SerialHandler
from src.common.models.path import Path
from src.common.movement.direction import Direction
from src.common.movement.drive import Drive
from src.common.movement.climb import Climb
from src.d_climb_stair.climber import Climber


def get_configuration():
    config_object = ConfigParser()
    config_object.read("../../resources/config.ini")
    return config_object["D_CLIMB_STAIR"]


def get_fake_path():
    # TODO: Get path from state machine.
    path = Path()
    path.add_instruction(Direction.DRIVE_LEFT, 20)
    path.add_instruction(Direction.DRIVE_RIGHT, 10)
    path.add_instruction(Direction.DRIVE_RIGHT, 0)
    path.add_instruction(Direction.DRIVE_LEFT, 50)
    path.add_instruction(Direction.DRIVE_LEFT, 0)
    path.add_instruction(Direction.DRIVE_RIGHT, 70)
    return path


def run(path: Path):
    try:
        conf = get_configuration()
        handler = SerialHandler()
        drive = Drive(handler)
        climb = Climb(handler)
        climber = Climber(conf, drive, climb)
        result = climber.move(path)
        print("Clearing the stair was " + ("successful." if result else "unsuccessful."))
    except Exception:
        print("Error in course_climb_stair")


if __name__ == '__main__':
    run(get_fake_path())
