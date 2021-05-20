from src.common.models.instruction import Instruction
from src.common.movement.direction import Direction


class Path:
    def __init__(self):
        self.instructions = []

    def add_instruction(self, direction: Direction, distance: int):
        """
        Add the given instructino to the list
        :param direction: Enum Direction
        :param distance: int
        """
        self.instructions.append(Instruction(direction, distance))

    def get_final_position(self):
        """
        Determine theoretical position of the robot after clearing the path.
        :return: int - position
        """
        center = 750  # Center of stair
        position = center
        for i in self.instructions:
            if i.direction == Direction.DRIVE_LEFT:
                position -= i.distance
            else:
                position += i.distance
        return position

    def to_string(self):
        s = ""
        counter = 0
        for ins in self.instructions:
            counter += 1
            s += "{}. ".format(counter)
            s += ins.direction.name
            s += " - "
            s += str(int(ins.distance)) + " mm and go up"
            s += "\n"
        return s
