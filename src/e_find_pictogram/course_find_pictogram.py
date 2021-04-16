from src.common.communication.serial_handler import SerialHandler
from src.common.models.instruction import Instruction
from src.common.movement.direction import Direction
from src.common.movement.drive import Drive


def get_instruction(position_pictogram: int, position_robot: int):
    distance = abs(position_robot - position_pictogram)
    if position_robot - position_pictogram > 0:
        return Instruction(Direction.DRIVE_LEFT, distance)
    else:
        return Instruction(Direction.DRIVE_RIGHT, distance)


def get_position_pictogram(pictogram):
    pictograms = ['hammer', 'sandwich', 'rule', 'paint', 'pencil']
    if pictogram == "hammer":
        return 10
    elif pictogram == "sandwich":
        return 20
    elif pictogram == "rule":
        return 30
    elif pictogram == "paint":
        return 40
    elif pictogram == "pencil":
        return 50
    else:
        raise Exception("The pictogram '{}' must be in {}".format(pictogram, pictograms))


def run(pictogram, position_robot):
    try:
        handler = SerialHandler()
        drive = Drive(handler)
        position_pictogram = get_position_pictogram(pictogram)
        instruction: Instruction = get_instruction(position_pictogram, position_robot)
        drive.move(instruction.direction, instruction.distance)
        drive.forward(20)
        return True
    except Exception:
        print("Error in course_find_pictogram")
        return False


if __name__ == '__main__':
    run("hammer", 60)
