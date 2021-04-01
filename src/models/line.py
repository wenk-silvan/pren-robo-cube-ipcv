from src.models.point import Point
import logging


class Line:
    def __init__(self, p1, p2):
        if not isinstance(p1, Point) and not isinstance(p2, Point):
            logging.error("The provided object is not of type Point.")
            return
        self.p1 = p1
        self.p2 = p2
