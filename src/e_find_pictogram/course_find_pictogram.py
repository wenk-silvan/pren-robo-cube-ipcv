from src.common.communication.serial_handler import SerialHandler
from src.common.models.instruction import Instruction
from src.common.movement.direction import Direction
from src.common.movement.drive import Drive
from configparser import ConfigParser
import logging


def get_instruction(position_pictogram: int, position_robot: int):
    distance = abs(position_robot - position_pictogram)
    if position_robot > position_pictogram:
        return Instruction(Direction.DRIVE_LEFT, distance)
    else:
        return Instruction(Direction.DRIVE_RIGHT, distance)


def get_position_pictogram(conf, pictogram):
    pictograms = ['hammer', 'sandwich', 'rule', 'paint', 'pencil']
    if pictogram == "hammer":
        return int(conf["position_hammer"])
    elif pictogram == "sandwich":
        return int(conf["position_sandwich"])
    elif pictogram == "rule":
        return int(conf["position_rule"])
    elif pictogram == "paint":
        return int(conf["position_paint"])
    elif pictogram == "pencil":
        return int(conf["position_pencil"])
    else:
        raise RuntimeError("The pictogram '{}' must be in {}".format(pictogram, pictograms))


def run(conf, pictogram, position_robot, drive: Drive):
    try:
        position_pictogram = get_position_pictogram(conf, pictogram)
        instruction: Instruction = get_instruction(position_pictogram, position_robot)
        drive.move(instruction.direction, instruction.distance)
        drive.forward(20)
        return True
    except RuntimeError as e:
        logging.error("Error in e_find_pictogram:\n", e)
        return False


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    conf_parser = ConfigParser()
    conf_parser.read("resources/config.ini")
    serial = SerialHandler()
    run(conf_parser["E_FIND_PICTOGRAM"], "hammer", 60, Drive(serial))
