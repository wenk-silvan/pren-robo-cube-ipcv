import cv2


class FakeCamera:
    def __init__(self):
        pass

    def __exit__(self):
        pass

    def snapshot(self):
        """
        Read the current frame and resize to 1280x980
        :return:
        """
        return cv2.resize(cv2.imread("../../../images/stair/back_left_pictos/img019.jpg"), (1280, 980))
