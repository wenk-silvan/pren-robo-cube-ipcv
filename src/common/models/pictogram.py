from src.common.models.point import Point
import logging


class Pictogram:
    def __init__(self, top_left: Point, bottom_right: Point, cascade_index):
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.name, self.position = self._get_by_index(cascade_index)

    def _get_by_index(self, cascade_index):
        if cascade_index == 0:
            return "hammer", 180
        elif cascade_index == 1:
            return "sandwich", 430
        elif cascade_index == 2:
            return "rule", 680
        elif cascade_index == 3:
            return "paint", 930
        elif cascade_index == 4:
            return "pencil", 1180
        else:
            logging.error("The cascade index '{}' must be between 0 and 4.".format(cascade_index))
