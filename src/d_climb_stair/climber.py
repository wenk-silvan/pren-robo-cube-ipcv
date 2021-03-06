import logging

from src.common.models.path import Path
from src.common.movement.climb import Climb
from src.common.movement.drive import Drive


class Climber:
    def __init__(self, conf, drive: Drive, climb: Climb):
        self.drive = drive
        self.climb = climb
        self.duration = int(conf["stair_step_height_mm"]) / 2  # TODO: Use accurate duration
        self.forward_head_mm = int(conf["climb_forward_head_mm"])
        self.forward_body_mm = int(conf["climb_forward_body_mm"])
        self.forward_tail_mm = int(conf["climb_forward_tail_mm"])

    def move(self, path: Path) -> object:
        """
        Attemps to clear the stair using the given path.
        :param path: Path: Contains a list of instructions with direction and distance.
        :return: True or False whether the path could be cleared.
        """
        try:
            logging.info("Move until sensor stops")
            # self.drive.forward_to_object(self.forward_head_mm + 2)
            self.drive.forward(110)  # first tests, just bump into stair.
            self.drive.backward(1)
            for instruction in path.instructions:
                logging.info("Move %s mm in direction %s", instruction.distance, instruction.direction)
                self.drive.move(instruction.direction, instruction.distance)
                self._step_up()
            return True

        except Exception:
            return False

    def _step_down(self):
        raise NotImplementedError

    def _step_up(self):
        logging.info("Try to climb next step")
        self.drive.backward(1)  # move slightly away from the stair
        self.climb.body_down_slow(5)

        self.climb.head_up_fast(150)
        self.drive.forward_slow(20)
        self.climb.head_down_slow(5)
        self.drive.backward(1)
        
        self.climb.body_up_fast(95)
        self.drive.forward_slow(20)
        self.drive.backward(1)
        
        self.climb.tail_up_fast(95)
        self.drive.forward_slow(20)
        logging.info("Step climbed successfully.")
