from configparser import ConfigParser
import logging
from src.common.communication.serial_handler import SerialHandler
from src.common.models.path import Path
from src.common.movement.direction import Direction
from src.common.movement.drive import Drive
from src.common.movement.climb import Climb
from src.d_climb_stair.climber import Climber


def get_fake_path():
    path = Path()
    path.add_instruction(Direction.DRIVE_LEFT, 20)
    path.add_instruction(Direction.DRIVE_RIGHT, 10)
    path.add_instruction(Direction.DRIVE_RIGHT, 0)
    path.add_instruction(Direction.DRIVE_LEFT, 50)
    path.add_instruction(Direction.DRIVE_LEFT, 0)
    path.add_instruction(Direction.DRIVE_RIGHT, 70)
    return path


def run(conf, path: Path):
    try:
        handler = SerialHandler()
        drive = Drive(handler)
        climb = Climb(handler)
        climber = Climber(conf, drive, climb)
        result = climber.move(path)
        logging.info("Clearing the stair was " + ("successful." if result else "unsuccessful."))
    except RuntimeError as e:
        logging.error("Error in d_climb_stair:\n", e)


if __name__ == '__main__':
    conf_parser = ConfigParser()
    conf_parser.read("resources/config.ini")
    run(conf_parser["D_CLIMB_STAIR"], get_fake_path())
