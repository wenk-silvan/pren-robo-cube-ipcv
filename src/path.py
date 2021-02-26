from instruction import Instruction
from src.direction import Direction


class Path:
    def __init__(self):
        self.instructions = []

    def add_instruction(self, direction, distance):
        self.instructions.append(Instruction(direction, distance))

    def to_string(self):
        s = ""
        for ins in self.instructions:
            s += ins.direction.name
            s += " - "
            s += str(int(ins.distance)) + " mm"
            s += "\n"
        return s
