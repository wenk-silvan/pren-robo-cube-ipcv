import time

import imutils
from imutils.video.pivideostream import PiVideoStream


class Camera:
    def __init__(self):
        self.stream = PiVideoStream()
        self.stream.start()
        time.sleep(1)

    def __exit__(self):
        self.stream.stop()

    def snapshot(self):
        frame = self.stream.read()
        return imutils.resize(image=frame, width=1280, height=960)
