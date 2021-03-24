import numpy as np
import cv2
from line import Line
from camera import Camera
from pathfinder import Pathfinder


class StairDetection:
    def __init__(self, configuration):
        self.camera = Camera(configuration)
        self.conf = configuration
        pass

    def detect_stair(self):
        # image = self.camera.snapshot()
        image = cv2.imread(self.conf["img_path"])
        line = self.detect_yellow_line(image)
        is_center = StairDetection.is_centered(line, image, int(self.conf["staircase_yellow_width_offset"]))
        return is_center

    def detect_yellow_line(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hsv_lower_range = (20, 80, 40)
        hsv_upper_range = (60, 255, 255)
        thresh = cv2.inRange(hsv, hsv_lower_range, hsv_upper_range)

        lines = cv2.HoughLinesP(
            thresh,
            rho=int(self.conf["staircase_lines_rho"]),
            theta=1 * np.pi / 180,
            minLineLength=thresh.shape[0] / 5,
            maxLineGap=thresh.shape[1],
            threshold=int(self.conf["staircase_yellow_lines_thresh"]),
        )

        lines = Pathfinder.remove_skew_lines(lines, int(self.conf["staircase_max_skewness"]))
        lines = StairDetection.remove_off_place_lines(lines, thresh.shape)
        # Pathfinder.draw_lines(lines, image)
        # cv2.imshow("Result", image)
        # cv2.waitKey(0)
        return StairDetection.select_widest_line(lines)

    @staticmethod
    def is_centered(line, image, offset):
        width = image.shape[1]
        center = (line.p1x <= offset) and (line.p2x >= width - offset)
        return center

    @staticmethod
    def remove_off_place_lines(lines, img_shape):
        return list(filter(lambda l: l[1] > (3/4) * img_shape[0], lines))  # only lines from bottom quarter of image

    @staticmethod
    def select_widest_line(lines):
        line = max(lines, key=lambda l: l[2] - l[0])
        return Line((line[0], line[1]), (line[2], line[3]))
