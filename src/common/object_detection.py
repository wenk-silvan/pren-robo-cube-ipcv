import logging

import cv2

from src.common.models.obstacle import Obstacle
from src.common.models.pictogram import Pictogram
from src.common.models.point import Point


class ObjectDetection:
    def __init__(self, path_to_cascade, cascade_names):
        self.cascades = []
        for c in cascade_names:
            self.cascades.append(cv2.CascadeClassifier(path_to_cascade + c))

    def detect_obstacles(self, img, min_area, max_area, scale, neighbours):
        # TODO: Replace with real obstacle detection.
        objects = [(854, 526), (1006, 603)], [(602, 278), (722, 302)], [(803, 344), (924, 377)], [(834, 724), (1070, 818)], \
                  [(238, 523), (414, 620)], [(809, 246), (910, 305)], [(311, 401), (432, 487)]
        return [Obstacle(Point(o[0][0], o[0][1]), Point(o[1][0], o[1][1])) for o in objects]

    def detect_pictograms(self, img, min_area, max_area, scale, neighbours):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        objects = []
        for c in self.cascades:
            try:
                detected = c.detectMultiScale(gray, scale, neighbours)
                for (x, y, w, h) in detected:
                    area = w * h
                    if min_area < area < max_area:
                        objects.append(Pictogram(Point(x, y), Point(x + w, y + h), self.cascades.index(c)))
            except Exception as err:
                logging.error(err)
                return []
        return objects

    def draw(self, img, objects, color):
        [cv2.rectangle(img, (p1.x, p1.y), (p2.x, p2.y), color, 2) for (p1, p2) in objects]

    def draw_objects(self, img, objects, color):
        [cv2.rectangle(img, (p.top_left.x, p.top_left.y), (p.bottom_right.x, p.bottom_right.y), color, 2) for p in
         objects]
