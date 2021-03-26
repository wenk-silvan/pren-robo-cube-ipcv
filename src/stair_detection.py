import numpy as np
import cv2
import logging
from line import Line
from camera import Camera
from pathfinder import Pathfinder
from direction import Direction


class StairDetection:
    def __init__(self, configuration):
        self.camera = Camera(configuration)
        self.conf = configuration
        self.first_step = None
        pass

    def detect_stair(self):
        # image = self.camera.snapshot()
        image = cv2.imread(self.conf["img_path"])
        line = self.detect_yellow_line(image)
        is_center = StairDetection.is_centered(line, image, int(self.conf["staircase_yellow_width_offset"]))
        return is_center

    def detect_first_step(self, image):
        return self.detect_yellow_line(image)

    def detect_yellow_line(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        hsv_lower_range = (0, 56, 47)
        hsv_upper_range = (100, 176, 200)
        thresh = cv2.inRange(hsv, hsv_lower_range, hsv_upper_range)

        lines = cv2.HoughLinesP(
            thresh,
            rho=int(self.conf["staircase_lines_rho"]),
            theta=1 * np.pi / 180,
            minLineLength=thresh.shape[0] / 5,
            maxLineGap=thresh.shape[1],
            threshold=int(self.conf["staircase_yellow_lines_thresh"]),
        )

        lines = Pathfinder.remove_skew_lines(lines, 200)
        # lines = Pathfinder.remove_skew_lines(lines, int(self.conf["staircase_max_skewness"]))
        lines = StairDetection.remove_off_place_lines(lines, thresh.shape)
        Pathfinder.draw_lines(lines, image)
        cv2.imshow("Result", image)
        cv2.waitKey(0)
        return StairDetection.select_widest_line(lines)

    def get_angle(self, line, image):
        pass

    def is_centered(self):
        if self.first_step is None:
            return False

        return True

    @staticmethod
    def get_next_movement(line, image):
        if not isinstance(line, Line):
            logging.error("The provided object is not of type Line.")
            return

        if line.p1y <= line.p2y + 5 or line.p1y >= line.p2y:  # line is straight
            if line.p1x > 20 and line.p2x > image.shape[0] - 20:  # line is too far right
                return Direction.DRIVE_RIGHT
            elif line.p1x < 20 and line.p2x < image.shape[0] - 20:  # line is too far left
                return Direction.DRIVE_LEFT
            elif line.p1x > 20 and line.p2x < image.shape[0] - 20:  # line is too far away
                return Direction.DRIVE_FORWARD
            else:
                return Direction.DRIVE_BACK

        elif line.p1y > line.p2y + 5:  # line is right-skewed
            return Direction.ROTATE_RIGHT

        elif line.p1y < line.p2y - 5:  # line is left-skewed
            return Direction.ROTATE_LEFT

        else:
            logging.error("The line has an unexpected state in the image.")

    @staticmethod
    def line_is_in_range(line, image, offset):
        width = image.shape[1]
        center = (line.p1x <= offset) and (line.p2x >= width - offset)
        return center

    @staticmethod
    def remove_off_place_lines(lines, img_shape):
        return list(filter(lambda l: l[1] > (3 / 4) * img_shape[0], lines))  # only lines from bottom quarter of image

    @staticmethod
    def select_widest_line(lines):
        if lines is None or len(lines) == 0:
            return None
        line = max(lines, key=lambda l: l[2] - l[0])
        return Line((line[0], line[1]), (line[2], line[3]))
