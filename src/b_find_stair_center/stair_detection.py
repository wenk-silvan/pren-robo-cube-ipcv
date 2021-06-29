import numpy as np
import logging
import cv2

from src.common.models.line import Line
from src.common.models.pictogram import Pictogram
from src.common.models.point import Point
from src.common.movement.direction import Direction
from src.b_find_stair_center.image_processing import ImageProcessing


class StairDetection:
    def __init__(self, configuration, image_processor: ImageProcessing):
        self.conf = configuration
        self.image_processor = image_processor

    def detect_lines(self, image):
        """
        Detect lines of stair in the given image.
        :param image: The image in where to find the stair.
        :return:
            lines_vertical (Line[]): All vertical lines found in the image using given parameters. Should be handlebars.
            lines_horizontal (Line[]): All horizontal lines found in the image using given parameters. Should be steps.
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
        :param pictograms: List of Pictogram.
        :param can_see_obstacles: True if obstacles were detected, false if not.
        :return:
            direction (Direction): The direction of the next movement.
            value (int): The value by which should be moved. Either angle for rotating or millimeters for driving.
            is_centered (boolean): Flag whether the robot is in the correct spot to move on to pathfinding.
        """
        rotation_angle = int(self.conf["rotation_angle"])
        if len(pictograms) >= 3:
            return Direction.DRIVE_FORWARD, 0, True
        else:
            return Direction.ROTATE_BODY_RIGHT, rotation_angle, False


        # max_angle = float(self.conf["stair_straight_max_angle"])
        # rotation_angle = int(self.conf["rotation_angle"])
        # can_see_pictograms = len(pictograms) > 0
        # border_offset = int(self.conf["stair_border_offset"])
        # end_left = border_offset
        # end_right = image.shape[1] - border_offset

        # if not can_see_obstacles or len(lines_horizontal) < 1:
        #     logging.info("Detection: No pictograms and obstacles found -> Rotate right")
        #     return Direction.ROTATE_BODY_LEFT, rotation_angle, False  # stair not found

        # inters_left, inters_right = self._calculate_intersections(lines_vertical, lines_horizontal, pictograms[0].position)
        # blx, brx, angle = self._calculate_stair_position(image.shape[1], inters_left, inters_right, lines_horizontal[0])

        # TODO: Fine tune measurements
        # bottom_line = lines_horizontal[0]
        # angle = self._get_angle(bottom_line)
        # pictogram_width = 60
        # perspective_offset = 250
        # horizontal_tolerance = 20
        # pictogram_top_gap = 100
        # mm_per_px = 0.313

        # if angle <= max_angle:  # stair is straight
        #     if not can_see_pictograms:  # stair is too close
        #         logging.info("Detection: Stair is straight, no pictos found -> Drive back")
        #         return Direction.DRIVE_BACK, 10, False
        #     pictogram: Pictogram = pictograms[0]
        #     drive_distance = pictogram.top_left.x - perspective_offset - pictogram.position + (pictogram_width / 2)
        #     logging.info("Drive distance = %s = %s - %s - %s + (%s / 2)", drive_distance, pictogram.top_left.x, perspective_offset, pictogram.position, pictogram_width)
        #     if pictogram_top_gap < pictogram.top_left.y:  # stair is too far away
        #         logging.info("Detection: Stair is straight, pictos found, too far away -> Drive forward")
        #         return Direction.DRIVE_FORWARD, 20, False
        #     elif drive_distance > horizontal_tolerance:  # stair is straight but too far right
        #         logging.info("Detection: Stair is straight, pictos found, robo too far left -> Drive right")
        #         return Direction.DRIVE_RIGHT, drive_distance * mm_per_px, False
        #     elif drive_distance < -horizontal_tolerance:  # stair is straight but too far left
        #         logging.info("Detection: Stair is straight, pictos found, robo too far right -> Drive left")
        #         return Direction.DRIVE_LEFT, abs(drive_distance) * mm_per_px, False
        #     else:  # stair is centered
        #         return Direction.DRIVE_FORWARD, 0, True

        # else:
        #     logging.info("Bottom Line - Left: %s,%s - Right %s,%s", bottom_line.p1.x, bottom_line.p1.y, bottom_line.p2.x, bottom_line.p2.y)
        #     if bottom_line.p1.y < bottom_line.p2.y:  # stair is skew to the left
        #         logging.info("Detection: Stair is skew to the right, pictos found -> Rotate right")
        #         return Direction.ROTATE_BODY_RIGHT, rotation_angle, False
        #     elif bottom_line.p1.y > bottom_line.p2.y:  # stair is skew to the right
        #         logging.info("Detection: Stair is skew to the left, pictos found -> Rotate left")
        #         return Direction.ROTATE_BODY_LEFT, rotation_angle, False
        #     else:
        #         logging.error("Stair position is in an unexpected state.")

    def _get_angle(self, line: Line):
        angle_rad = np.math.atan2(abs(line.p1.y - line.p2.y), abs(line.p1.x - line.p2.x))
        return angle_rad * 180 / np.pi

    def _calculate_intersections(self, lines_vertical, lines_horizontal, pivot):
        inters_left = []
        inters_right = []
        for line_horizontal in lines_horizontal:
            intersections = self._get_line_intersections(line_horizontal, lines_vertical)
            inters_left_local = list(filter(lambda i: i.x < pivot, intersections))
            inters_right_local = list(filter(lambda i: i.x >= pivot, intersections))
            if len(inters_left_local) > 0:
                inters_left.append(max(inters_left_local, key=lambda i: abs(pivot - i.x)))
            if len(inters_right_local) > 0:
                inters_right.append(max(inters_right_local, key=lambda i: abs(pivot - i.x)))
        return inters_left, inters_right

    def _get_line_intersections(self, line_a, lines_vertical):
        intersections = []
        for line_b in lines_vertical:
            if not self.image_processor.line_segments_intersect(line_a, line_b):
                continue
            intersections.append(self.image_processor.line_intersection(line_a, line_b))
        return intersections

    def _detect_handlebars(self, lines):
        lines = StairDetection._remove_skew_lines(lines, int(self.conf["bars_lines_min_angle"]),
                                                  int(self.conf["bars_lines_max_angle"]))
        lines.sort(key=lambda l: l.p1.x, reverse=False)  # sort lines by x1 from left to right
        return StairDetection._remove_horizontally_close_lines(lines, int(self.conf["bars_lines_min_line_gap"]))

    def _detect_steps(self, lines, img_height):
        lines = StairDetection._remove_skew_lines(lines, int(self.conf["steps_lines_min_angle"]),
                                                  int(self.conf["steps_lines_max_angle"]))
        lines.sort(key=lambda l: l.p1.y, reverse=True)  # sort lines by y1 from bottom to top
        lines = StairDetection._remove_vertically_close_lines(lines, img_height,
                                                             int(self.conf["steps_lines_min_line_gap"]))
        return StairDetection._remove_outlier_lines(lines)

    @staticmethod
    def _calculate_stair_position(img_width, intersections_left, intersections_right, bottom_line):
        left_end = Point(0, 0)
        right_end = Point(0, 0)
        intersections_left.sort(key=lambda i: i.y, reverse=True)
        intersections_right.sort(key=lambda i: i.y, reverse=True)

        angle_rad = np.math.atan2(abs(bottom_line.p1.y - bottom_line.p2.y), abs(bottom_line.p1.x - bottom_line.p2.x))
        angle = angle_rad * 180 / np.pi

        # at least two intersections required to make sure it is left side of stair
        if len(intersections_left) >= 2:
            # left_end = intersections_left[0]
            left_end = min(intersections_left, key=lambda i: i.x)
        else:
            left_end.x = 0
            left_end.y = bottom_line.p1.y

        # at least two intersections required to make sure it is right side of stair
        if len(intersections_right) >= 2:
            # right_end = intersections_right[0]
            right_end = max(intersections_right, key=lambda i: i.x)
        else:
            right_end.x = img_width
            right_end.y = bottom_line.p2.y
        return left_end.x, right_end.x, angle

    @staticmethod
    def _remove_horizontally_close_lines(lines, min_line_gap):
        previous_x1 = 0
        lines_not_close = []
        for l in lines:
            if (l.p1.x - previous_x1) >= min_line_gap:
                lines_not_close.append(l)
                previous_x1 = l.p1.x
        return lines_not_close

    @staticmethod
    def _remove_skew_lines(lines, min_angle, max_angle):
        return [l for l in lines
                if min_angle <= np.math.atan2(abs(l.p1.y - l.p2.y), abs(l.p1.x - l.p2.x)) * 180 / np.pi <= max_angle]

    @staticmethod
    def _remove_vertically_close_lines(lines, img_height, min_line_gap):
        previous_y1 = img_height
        lines_not_close = []
        for l in lines:
            if (previous_y1 - l.p1.y) >= min_line_gap:
                lines_not_close.append(l)
                previous_y1 = l.p1.y
        return lines_not_close

    @staticmethod
    def _remove_outlier_lines(lines):
        if len(lines) < 1: return lines
        min_skewness = 10
        lines_skew_left = [l for l in lines if l.p1.y - l.p2.y > 0]
        lines_skew_right = [l for l in lines if l.p1.y - l.p2.y < 0]
        y_distances_abs = [abs(l.p1.y - l.p2.y) for l in lines]
        avg_y_distance = sum(y_distances_abs) / len(y_distances_abs)
        if avg_y_distance < min_skewness:
            logging.info("No outlier lines found, none removed")
            return lines  # don't remove outliers if stair is already straight

        if len(lines_skew_left) <= 2 and len(lines_skew_right) >= 3:
            logging.info("Removed %s left-skewed outliers.", len(lines_skew_left))
            return lines_skew_right
        elif len(lines_skew_right) <= 2 and len(lines_skew_left) >= 3:
            logging.info("Removed %s right-skewed outliers.", len(lines_skew_right))
            return lines_skew_left
        logging.info("No outlier lines found, none removed")
        return lines
