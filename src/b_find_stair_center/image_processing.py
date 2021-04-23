import numpy as np
import cv2
from src.common.models.line import Line
from src.common.models.point import Point


class ImageProcessing:
    def __init__(self, configuration):
        self.conf = configuration

    def detect_lines_vertical(self, image):
        """
        Detects vertical hough lines in the image using the parameters of the config file (bars_*).
        :param image: The image
        :return: (Line[]) list of lines.
        """
        return ImageProcessing._detect_lines_probabilistic(
            image,
            int(self.conf["bars_lines_rho"]),
            int(self.conf["bars_lines_threshold"]),
            int(self.conf["bars_lines_min_line_length"]),
            int(self.conf["bars_lines_max_line_gap"]),
            int(self.conf["bars_canny_thresh_1"]),
            int(self.conf["bars_canny_thresh_2"])
        )

    def detect_lines_horizontal(self, image):
        """
        Detects horizontal hough lines in the image using the parameters of the config file (steps_*).
        :param image: The image
        :return: (Line[]) list of lines.
        """
        return ImageProcessing._detect_lines_probabilistic(
            image,
            int(self.conf["steps_lines_rho"]),
            int(self.conf["steps_lines_threshold"]),
            int(self.conf["steps_lines_min_line_length"]),
            int(self.conf["steps_lines_max_line_gap"]),
            int(self.conf["steps_canny_thresh_1"]),
            int(self.conf["steps_canny_thresh_2"])
        )

    def line_segments_intersect(self, l1: Line, l2: Line):
        """
        Checks whether the two lines intersect on a xy-coordinate system.
        :param l1: Line 1
        :param l2: Line 2
        :return: (boolean)
        """
        dir1: int = self._direction(l1.p1, l1.p2, l2.p1)
        dir2: int = self._direction(l1.p1, l1.p2, l2.p2)
        dir3: int = self._direction(l2.p1, l2.p2, l1.p1)
        dir4: int = self._direction(l2.p1, l2.p2, l1.p2)

        if dir1 != dir2 and dir3 != dir4:
            return True  # lines intersect
        if dir1 == 0 and self._is_point_on_line(l1, l2.p1):  # when p2 of line2 are on the line1
            return True
        if dir2 == 0 and self._is_point_on_line(l1, l2.p2):  # when p1 of line2 are on the line1
            return True
        if dir3 == 0 and self._is_point_on_line(l2, l1.p1):  # when p2 of line1 are on the line2
            return True
        if dir4 == 0 and self._is_point_on_line(l2, l1.p2):  # when p1 of line1 are on the line2
            return True
        return False

    def line_intersection(self, l1: Line, l2: Line):
        """
        Calculates point of intersection of two lines in a xy-coordinate system.
        :param l1: Line 1
        :param l2: Line 2
        :return: (Point) The point of intersection, if none found Point(0, 0) is returned.
        """
        x_diff = (l1.p1.x - l1.p2.x, l2.p1.x - l2.p2.x)
        y_diff = (l1.p1.y - l1.p2.y, l2.p1.y - l2.p2.y)

        div = self._determinant(x_diff, y_diff)
        if div == 0:  # lines do not intersect
            return Point(0, 0)

        d = self._determinant((l1.p1.x, l1.p1.y), (l1.p2.x, l1.p2.y)), \
            self._determinant((l2.p1.x, l2.p1.y), (l2.p2.x, l2.p2.y))
        x = self._determinant(d, x_diff) / div
        y = self._determinant(d, y_diff) / div
        return Point(x, y)

    @staticmethod
    def draw_lines(lines, image):
        """
        Draws the given lines on the given image using cv2.line(...)
        :param lines: The lines to draw
        :param image: The image.
        """
        for line in lines:
            p1 = (line.p1.x, line.p1.y)
            p2 = (line.p2.x, line.p2.y)
            cv2.line(image, p1, p2, (255, 0, 0), 2)

    @staticmethod
    def _detect_lines_probabilistic(image, rho, threshold, min_line_length, max_line_gap, canny1, canny2):
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
        if detected is None:
            return []
        return [Line(Point(l[0][0], l[0][1]), Point(l[0][2], l[0][3])) for l in detected]

    @staticmethod
    def _determinant(a, b):
        return a[0] * b[1] - a[1] * b[0]

    @staticmethod
    def _direction(a: Point, b: Point, c: Point):
        value: int = (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y)
        if value == 0:
            return 0  # co-linear
        elif value < 0:
            return 2  # anti-clockwise direction
        return 1  # clockwise direction

    @staticmethod
    def _is_point_on_line(l: Line, p: Point):
        return (p.x <= max(l.p1.x, l.p2.x) and p.x <= min(l.p1.x, l.p2.x) and
                (p.y <= max(l.p1.y, l.p2.y) and p.y <= min(l.p1.y, l.p2.y)))

    @staticmethod
    def _perpendicular(a):
        b = np.empty_like(a)
        b[0] = -a[1]
        b[1] = a[0]
        return b
