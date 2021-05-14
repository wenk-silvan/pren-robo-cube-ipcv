import logging

import cv2

from src.common.models.pictogram import Pictogram
from src.common.models.point import Point


class ObjectDetection:
    def __init__(self, path_to_cascade, cascade_names):
        self.cascades = []
        for c in cascade_names:
            self.cascades.append(cv2.CascadeClassifier(path_to_cascade + c))

    def detect(self, img, min_area, max_area, scale, neighbours):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        objects = []
        for c in self.cascades:
            try:
                detected = c.detectMultiScale(gray, scale, neighbours)
                for (x, y, w, h) in detected:
                    area = w * h
                    if min_area < area < max_area:
                        objects.append((Point(x, y), Point(x + w, y + h)))
            except Exception as err:
                logging.error(err)
                return []
        return objects

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

    def draw_pictograms(self, img, pictograms, color):
        [cv2.rectangle(img, (p.top_left.x, p.top_left.y), (p.bottom_right.x, p.bottom_right.y), color, 2) for p in pictograms]
