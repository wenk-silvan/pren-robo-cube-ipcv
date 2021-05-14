import cv2
import numpy as np

from src.common.image_manipulator import ImageManipulator


def _pass(_):
    pass


if __name__ == '__main__':
    cv2.namedWindow("Controls")
    cv2.createTrackbar("canny1", "Controls", 10, 255, _pass)
    cv2.createTrackbar("canny2", "Controls", 100, 255, _pass)
    cv2.createTrackbar("thresh", "Controls", 10, 255, _pass)
    cv2.createTrackbar("mll", "Controls", 10, 600, _pass)
    cv2.createTrackbar("mlg", "Controls", 10, 600, _pass)
    img = cv2.resize(cv2.imread("../../../images/stair/pathfinding/06/img001.jpg"), (1280, 960))
    image_manipulator = ImageManipulator(img)
    image = image_manipulator.transform_to_2d((600, 600))

    while True:
        img = image.copy()
        blurred = cv2.GaussianBlur(img, (5, 5), 0, 0)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        # ret, bin_img = cv2.threshold(gray, cv2.getTrackbarPos("bin1", "Controls"), cv2.getTrackbarPos("bin2", "Controls"), cv2.THRESH_BINARY)
        edges = cv2.Canny(gray, cv2.getTrackbarPos("canny1", "Controls"), cv2.getTrackbarPos("canny2", "Controls"))
        detected = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=1 * np.pi / 180,
            threshold=cv2.getTrackbarPos("thresh", "Controls"),
            minLineLength=cv2.getTrackbarPos("mll", "Controls"),
            maxLineGap=cv2.getTrackbarPos("mlg", "Controls")
        )
        for [(x1, y1, x2, y2)] in detected:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        cv2.imshow("Edges", edges)
        cv2.imshow("Result", img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:  # ESC
            break
