import cv2
import numpy as np

from src.common.image_manipulator import ImageManipulator


def _pass(_):
    pass


if __name__ == '__main__':
    cv2.namedWindow("Controls")
    cv2.createTrackbar("blockSize", "Controls", 2, 10, _pass)
    cv2.createTrackbar("ksize", "Controls", 3, 10, _pass)
    image_manipulator = ImageManipulator(cv2.imread("../../images/stair/pathfinding/01/img001.jpg"))
    image = image_manipulator.transform_to_2d((600, 600))

    while True:
        img = image.copy()
        blurred = cv2.GaussianBlur(img, (5, 5), 0, 0)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        gray = np.float32(gray)
        dst = cv2.cornerHarris(
            gray,
            cv2.getTrackbarPos("blockSize", "Controls"),
            5,
            0.2
        )

        # result is dilated for marking the corners, not important
        dst = cv2.dilate(dst, None)
        # Threshold for an optimal value, it may vary depending on the image.
        img[dst > 0.01 * dst.max()] = [0, 0, 255]
        cv2.imshow('dst', img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:  # ESC
            cv2.destroyAllWindows()
