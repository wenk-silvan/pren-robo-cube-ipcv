import time
import imutils
import cv2


class Camera:
    def __init__(self):
        self.stream = cv2.VideoCapture(0)
        self.stream.set(3, 1280)
        self.stream.set(4, 960)
        time.sleep(1)

    def __exit__(self):
        self.stream.stop()

    def snapshot(self):
        """
        Read the current frame and resize to 1280x980
        :return:
        """
        _, frame = self.stream.read()
        print(frame)
        flipped_frame = cv2.flip(frame, -1)  # flip vertically
        return imutils.resize(image=flipped_frame, width=1280, height=960)
