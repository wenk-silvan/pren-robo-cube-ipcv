import cv2
import logging

path_to_cascades = "../../resources/cascades/pictogram/"
paths = ['hammer.xml', 'sandwich.xml', 'rule.xml', 'paint.xml', 'pencil.xml']


class PictogramDetection:
    def __init__(self, ):
        self.cascades = []
        for c in paths:
            self.cascades.append(cv2.CascadeClassifier(path_to_cascades + c))

    def detect_and_draw(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        work = gray
        objects = []

        for c in self.cascades:
            objects = c.detectMultiScale(work, 1.15, 3)
            for (x, y, w, h) in objects:
                p1 = (x, y)
                p2 = (x + w, y + h)
                cv2.rectangle(img, p1, p2, (0, 0, 255), 2)

                # area = w * h
                # if area > 400:
                #   pass

        return objects
