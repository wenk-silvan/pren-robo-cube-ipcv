import logging

import cv2

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
            detected = c.detectMultiScale(gray, scale, neighbours)
            for (x, y, w, h) in detected:
                area = w * h
                if min_area < area < max_area:
                    objects.append((Point(x, y), Point(x + w, y + h)))
        return objects

    def draw(self, img, objects, color):
        [cv2.rectangle(img, (p1.x, p1.y), (p2.x, p2.y), color, 2) for (p1, p2) in objects]
