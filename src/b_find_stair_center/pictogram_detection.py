import cv2
import logging

from src.models.point import Point

path_to_cascades = "../../resources/cascades/pictogram/"
paths = ['hammer.xml', 'sandwich.xml', 'rule.xml', 'paint.xml', 'pencil.xml']


class PictogramDetection:
    def __init__(self, ):
        self.cascades = []
        for c in paths:
            self.cascades.append(cv2.CascadeClassifier(path_to_cascades + c))

    def detect(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        pictograms = []
        for c in self.cascades:
            objects = c.detectMultiScale(gray, 1.15, 3)
            for (x, y, w, h) in objects:
                area = w * h
                if 1000 < area < 15000:
                    pictograms.append((Point(x, y), Point(x + w, y + h)))
        return pictograms

    def draw(self, img, pictograms):
        color = (0, 0, 255)
        [cv2.rectangle(img, (p1.x, p1.y), (p2.x, p2.y), color, 2) for (p1, p2) in pictograms]
