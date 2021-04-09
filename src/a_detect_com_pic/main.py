import cv2
import pyttsx3
import logging
import time
from console_progressbar import ProgressBar

from src.common.camera.camera import Camera

logging.basicConfig(level=logging.INFO)

# TODO Move config-elements to config.ini
################################################################
path_to_cascades = "../../resources/cascades/pictogram/"
paths = ['hammer.xml', 'sandwich.xml', 'rule.xml', 'paint.xml', 'pencil.xml']  # PATH OF THE CASCADE
objectNames = ['hammer', 'sandwich', 'rule', 'paint', 'pencil']  # OBJECT NAMES TO DISPLAY
objectCount = 21  # how many objects to count for recognition
#################################################################


class PictogramDetector:

    def __init__(self):
        self.camera = Camera()
        self.pb = ProgressBar(total=objectCount, prefix='Detection', length=42, fill='=', zfill=' ')

        # LOAD THE CLASSIFIERS
        self.cascades = []
        for c in paths:
            self.cascades.append(cv2.CascadeClassifier(path_to_cascades + c))

        logging.info("Ready for detection")

    def detect(self):
        time.sleep(1)
        counter = 0
        stats = {'hammer': 0, 'sandwich': 0, 'rule': 0, 'paint': 0, 'pencil': 0}

        while counter < objectCount:
            image = self.camera.snapshot()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            work = gray
            for c in self.cascades:
                objects = c.detectMultiScale(work, 1.15, 3)
                for (x, y, w, h) in objects:
                    area = w * h
                    if area > 400:
                        o = objectNames[self.cascades.index(c)]
                        counter += 1
                        stats[o] += 1
                        logging.debug(o)
                        self.pb.print_progress_bar(counter)
        return stats


def main():
    detector = PictogramDetector()
    stats = detector.detect()
    logging.debug(stats)
    result = max(stats, key=stats.get)

    t2s = pyttsx3.init()
    t2s.setProperty('voice', t2s.getProperty('voices'))
    comb = 'some' if result is 'paint' else 'a'
    t2s.say("I am looking for %s %s" % (comb, result))
    t2s.runAndWait()


if __name__ == '__main__':
    main()
