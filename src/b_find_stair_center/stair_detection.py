import numpy as np
import logging

from src.common.models.line import Line
from src.common.models.point import Point
from src.common.movement.direction import Direction
from src.b_find_stair_center.image_processing import ImageProcessing


def _remove_skew_lines(lines, min_angle, max_angle):
    return [[x1, y1, x2, y2] for x1, y1, x2, y2 in lines
            if min_angle <= np.math.atan2(abs(y1 - y2), abs(x1 - x2)) * 180 / np.pi <= max_angle]


def _remove_horizontally_close_lines(lines, min_line_gap):
    previous_x1 = 0
    lines_not_close = []
    for x1, y1, x2, y2 in lines:
        if (x1 - previous_x1) >= min_line_gap:
            lines_not_close.append([x1, y1, x2, y2])
            previous_x1 = x1
    return lines_not_close


def _remove_vertically_close_lines(lines, img_height, min_line_gap):
    previous_y1 = img_height
    lines_not_close = []
    for x1, y1, x2, y2 in lines:
        if (previous_y1 - y1) >= min_line_gap:
            lines_not_close.append([x1, y1, x2, y2])
            previous_y1 = y1
    return lines_not_close


class StairDetection:
    def __init__(self, configuration, image_processor: ImageProcessing):
        self.conf = configuration
        self.image_processor = image_processor

    def detect_lines(self, image):
        """
        Detect lines of stair in the given image.
        :param image: The image in where to find the stair.
        :return:
            lines_vertical (array): All vertical lines found in the image using given parameters. Should be handlebars.
            lines_horizontal (array): All horizontal lines found in the image using given parameters. Should be steps.
        """
        lines_vertical = self.image_processor.detect_lines_vertical(image)
        lines_vertical = self._detect_handlebars(lines_vertical)
        lines_horizontal = self.image_processor.detect_lines_horizontal(image)
        lines_horizontal = self._detect_steps(lines_horizontal, image.shape[0])
        return lines_vertical, lines_horizontal

    def get_next_movement(self, image, lines_vertical, lines_horizontal, pictograms, can_see_obstacles):
        """
        Determine instruction for next movement by analyzing the given lines, pictograms and image.
        :param image: The image where the stair was searched.
        :param lines_vertical: All vertical lines found in the image using given parameters. Should be handlebars.
        :param lines_horizontal: All horizontal lines found in the image using given parameters. Should be steps.
        :param pictograms: List of detected pictograms. Each as a tuple of tl and br src.models.Point.
        :param can_see_obstacles: True if obstacles were detected, false if not.
        :return:
            direction (Direction): The direction of the next movement.
            value (int): The value by which should be moved. Either angle for rotating or millimeters for driving.
            is_centered (boolean): Flag whether the robot is in the correct spot to move on to pathfinding.
        """
        max_angle = int(self.conf["stair_straight_max_angle"])
        border_offset = int(self.conf["stair_border_offset"])
        end_left = border_offset
        end_right = image.shape[0] - border_offset
        rotation_angle = int(self.conf["rotation_angle"])
        drive_distance = int(self.conf["drive_distance"])

        if len(pictograms) < 1:
            if can_see_obstacles:  # stair is too close
                return Direction.DRIVE_BACK, drive_distance, False
            return Direction.ROTATE_BODY_RIGHT, rotation_angle, False  # stair not found

        inters_left, inters_right = self._calculate_intersections(lines_vertical, lines_horizontal, pictograms[0][1])
        blx, brx, angle = self._calculate_stair_position(image.shape[1], inters_left, inters_right, lines_horizontal[0])

        if angle <= max_angle:  # stair is straight
            if end_left < blx and end_right < brx:  # stair is too far right
                return Direction.DRIVE_RIGHT, drive_distance, False
            elif blx < end_left and brx < end_right:  # stair is too far left
                return Direction.DRIVE_LEFT, drive_distance, False
            elif end_left < blx and brx < end_right:  # stair is too far away
                return Direction.DRIVE_FORWARD, drive_distance, False
            elif blx <= end_left and end_right <= brx:  # stair is centered
                return Direction.DRIVE_FORWARD, 0, True
        elif lines_horizontal[0][1] < lines_horizontal[0][3]:
            return Direction.ROTATE_BODY_RIGHT, rotation_angle, False
        elif lines_horizontal[0][1] > lines_horizontal[0][3]:
            return Direction.ROTATE_BODY_LEFT, rotation_angle, False
        else:
            logging.error("Stair position is in an unexpected state.")

    def _calculate_intersections(self, lines_vertical, lines_horizontal, pivot: Point):
        inters_left = []
        inters_right = []
        for ax1, ay1, ax2, ay2 in lines_horizontal:
            line_horizontal = Line(Point(ax1, ay1), Point(ax2, ay2))
            intersections = self._get_line_intersections(line_horizontal, lines_vertical)

            inters_left_local = list(filter(lambda i: i.x < pivot.x, intersections))
            inters_right_local = list(filter(lambda i: i.x >= pivot.x, intersections))
            if len(inters_left_local) > 0:
                inters_left.append(min(inters_left_local, key=lambda i: abs(pivot.x - i.x)))
            if len(inters_right_local) > 0:
                inters_right.append(min(inters_right_local, key=lambda i: abs(pivot.x - i.x)))
        return inters_left, inters_right

    def _get_line_intersections(self, line_a, lines_vertical):
        intersections = []
        for bx1, by1, bx2, by2 in lines_vertical:
            line_b = Line(Point(bx1, by1), Point(bx2, by2))
            if not self.image_processor.line_segments_intersect(line_a, line_b):
                continue
            intersections.append(self.image_processor.line_intersection(line_a, line_b))
        return intersections

    def _calculate_stair_position(self, img_width, intersections_left, intersections_right, bottom_line):
        bl = Point(0, 0)
        br = Point(0, 0)
        intersections_left.sort(key=lambda i: i.y, reverse=True)
        intersections_right.sort(key=lambda i: i.y, reverse=True)

        angle_rad = np.math.atan2(abs(bottom_line[1] - bottom_line[3]), abs(bottom_line[0] - bottom_line[2]))
        angle = angle_rad * 180 / np.pi

        if len(intersections_left) > 0:
            bl = intersections_left[0]
        else:
            bl.x = 0
            bl.y = bottom_line[1]

        if len(intersections_right) > 0:
            br = intersections_right[0]
        else:
            br.x = img_width
            br.y = bottom_line[3]
        return bl.x, br.x, angle

    def _detect_handlebars(self, lines):
        lines = _remove_skew_lines(lines, int(self.conf["bars_lines_min_angle"]),
                                   int(self.conf["bars_lines_max_angle"]))
        lines.sort(key=lambda l: l[0], reverse=False)  # sort lines by x1 from left to right
        lines = _remove_horizontally_close_lines(lines, int(self.conf["bars_lines_min_line_gap"]))
        return lines

    def _detect_steps(self, lines, img_height):
        lines = _remove_skew_lines(lines, int(self.conf["steps_lines_min_angle"]),
                                   int(self.conf["steps_lines_max_angle"]))
        lines.sort(key=lambda l: l[1], reverse=True)  # sort lines by y1 from bottom to top
        lines = _remove_vertically_close_lines(lines, img_height, int(self.conf["steps_lines_min_line_gap"]))
        return lines
