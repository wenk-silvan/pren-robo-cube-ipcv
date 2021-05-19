#!/bin/python3
import cv2
import pyttsx3
import logging
import time

#from imutils.video.pivideostream import PiVideoStream

path_to_cascades = "resources/cascades/pictogram/"
paths = ['hammer.xml', 'sandwich.xml', 'rule.xml', 'paint.xml', 'pencil.xml']  # PATH OF THE CASCADE
objectNames = ['hammer', 'sandwich', 'rule', 'paint', 'pencil']  # OBJECT NAMES TO DISPLAY
objectCount = 21  # how many objects to count for recognition


class PictogramDetector:
    """
    Class loads cascade files, analyzes the video stream and detects pictograms in front of the camera.
    """

    def __init__(self):
        #self.vs = PiVideoStream().start()

        self.vs = cv2.VideoCapture(0)
        self.vs.set(3, 640)
        self.vs.set(4, 480)

        time.sleep(1)
        self.cascades = []
        for c in paths:  # LOAD THE CLASSIFIERS
            self.cascades.append(cv2.CascadeClassifier(path_to_cascades + c))

        logging.info("Ready for detection")

    def detect(self):
        """
        Used to detect and count pictograms.
        :return: statistics of detected pictograms
        """
        counter = 0
        stats = {'hammer': 0, 'sandwich': 0, 'rule': 0, 'paint': 0, 'pencil': 0}

        while counter < objectCount:
            ret, img = self.vs.read()
            img = cv2.flip(img, -1)
            #img = imutils.resize(frame)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # With all cascades check captured frame
            for c in self.cascades:
                objects = c.detectMultiScale(gray, 1.15, 3)

                # Calculate and check the size of every found object
                for (x, y, w, h) in objects:
                    area = w * h
                    if area > 400:
                        o = objectNames[self.cascades.index(c)]
                        counter += 1
                        stats[o] += 1

        #self.vs.stop()
        return stats


def run():
    """
    Runs the PictogramDetector.
    :return: the pictogram which had the most hits.
    """
    try:
        detector = PictogramDetector()
        stats = detector.detect()
        logging.debug(stats)
        result = max(stats, key=stats.get)

        t2s = pyttsx3.init()
        t2s.setProperty('voice', t2s.getProperty('voices'))
        comb = 'some' if result is 'paint' else 'a'
        t2s.say("I am looking for %s %s" % (comb, result))
        logging.info("detected: %s", result)
        t2s.runAndWait()
        return result
    except RuntimeError as e:
        logging.error("Error in a_detect_pictogram:\n", e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    run()

