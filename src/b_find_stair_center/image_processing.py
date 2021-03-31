import numpy as np
import cv2


def draw_lines(lines, img):
    for x1, y1, x2, y2 in lines:
        p1 = (x1, y1)
        p2 = (x2, y2)
        if not p1 or not p2:
            continue
        cv2.line(img, p1, p2, (255, 0, 0), 2)


def detect_lines_probabilistic(image, rho, threshold, min_line_length, max_line_gap, canny1, canny2):
    blurred = cv2.GaussianBlur(image, (5, 5), 0, 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(image=gray, threshold1=canny1, threshold2=canny2, apertureSize=3)
    detected = cv2.HoughLinesP(
        canny,
        rho=rho,
        theta=1 * np.pi / 180,
        threshold=threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap
    )
    return [[l[0][0], l[0][1], l[0][2], l[0][3]] for l in detected]


def perpendicular(a):
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b


class ImageProcessing:
    def __init__(self, configuration):
        self.conf = configuration

    def detect_lines_vertical(self, image):
        return detect_lines_probabilistic(
            image,
            int(self.conf["bars_lines_rho"]),
            int(self.conf["bars_lines_threshold"]),
            int(self.conf["bars_lines_min_line_length"]),
            int(self.conf["bars_lines_max_line_gap"]),
            int(self.conf["bars_canny_thresh_1"]),
            int(self.conf["bars_canny_thresh_2"])
        )

    def detect_lines_horizontal(self, image):
        return detect_lines_probabilistic(
            image,
            int(self.conf["steps_lines_rho"]),
            int(self.conf["steps_lines_threshold"]),
            int(self.conf["steps_lines_min_line_length"]),
            int(self.conf["steps_lines_max_line_gap"]),
            int(self.conf["steps_canny_thresh_1"]),
            int(self.conf["steps_canny_thresh_2"])
        )

    def intersection(self, a_p1, a_p2, b_p1, b_p2):
        da = a_p2 - a_p1
        db = b_p2 - b_p1
        dp = a_p1 - b_p1
        dap = perpendicular(da)
        denom = np.dot(dap, db)
        num = np.dot(dap, dp)
        return (num / denom) * db + b_p1
