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
        return cv2.imread("../../../images/stair/pathfinding/06/img001.jpg")
