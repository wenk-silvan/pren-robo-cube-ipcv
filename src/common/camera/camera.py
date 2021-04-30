import time
import imutils
from imutils.video.pivideostream import PiVideoStream
import cv2


class Camera:
    def __init__(self):
        self.stream = PiVideoStream()
        self.stream.start()
        time.sleep(1)

    def __exit__(self):
        self.stream.stop()

    def snapshot(self):
        """
        Read the current frame and resize to 1280x980
        :return:
        """
        frame = self.stream.read()
        flipped_frame = cv2.flip(frame, 0)  # flip vertically
        return imutils.resize(image=flipped_frame, width=1280, height=960)
