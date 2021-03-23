import cv2
from camera import Camera


class StairDetection:
    def __init__(self, configuration):
        self.camera = Camera(configuration)
        self.conf = configuration
        pass

    def detect_yellow_line(self, image):
        return False

    def detect_stair(self):
        image = self.camera.snapshot()
        return self.detect_yellow_line(image)

    def is_centered(self):
        detected = self.detect_stair()
        pass
