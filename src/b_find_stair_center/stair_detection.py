import numpy as np
import logging

from src.c_pathfinding.line import Line
from src.camera.camera import Camera
from src.movement.direction import Direction
from src.b_find_stair_center.image_processing import ImageProcessing


def _remove_skew_lines(lines, min_angle, max_angle):
    return [[x1, y1, x2, y2] for x1, y1, x2, y2 in lines
            if min_angle <= np.math.atan2(abs(y1 - y2), abs(x1 - x2)) * 180 / np.pi <= max_angle]


def _remove_horizontally_close_lines(lines, min_line_gap):
    previous_x1 = 0
    lines_not_close = []
    for x1, y1, x2, y2 in lines:
        if (previous_x1 - x1) >= min_line_gap:
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
    def __init__(self, configuration, image_processor, camera):
        if not isinstance(image_processor, ImageProcessing):
            logging.error("The provided object is not of type ImageProcessing.")
            return

        if not isinstance(camera, Camera):
            logging.error("The provided object is not of type Camera.")
            return

        self.camera = camera
        self.conf = configuration
        self.first_step = None
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

    def get_next_movement(self, image, lines_vertical, lines_horizontal):
        """
        Get instruction for next movement by analyzing the given lines of the image.
        :param image: The image where the stair was searched.
        :param lines_vertical: All vertical lines found in the image using given parameters. Should be handlebars.
        :param lines_horizontal: All horizontal lines found in the image using given parameters. Should be steps.
        :return:
            direction (Direction): The direction of the next movement.
            value (int): The value by which should be moved. Either angle for rotating or millimeters for driving.
            is_centered (boolean): Flag whether the robot is in the correct spot to move on to pathfinding.
        """
        inters_left, inters_right = self._calculate_intersections(lines_vertical, lines_horizontal)
        tl, tr, bl, br = self._calculate_stair_frame(inters_left, inters_right)
        blx, bly = bl
        brx, bry = br
        skewness_tolerance = 5
        border_offset = 20
        end_left = border_offset
        end_right = image.shape[0] - border_offset
        rotation_angle = 5
        drive_distance = 10

        if bl == (0, 0) and br == (0, 0):  # no stair found
            return Direction.ROTATE_RIGHT, rotation_angle, False
        elif bry - skewness_tolerance <= bly <= bry + skewness_tolerance:  # stair is straight
            if end_left < blx and end_right < brx:  # stair is too far right
                return Direction.DRIVE_RIGHT, drive_distance, False
            elif blx < end_left and brx < end_right:  # stair is too far left
                return Direction.DRIVE_LEFT, drive_distance, False
            elif end_left < blx and brx < end_right:  # stair is too far away
                return Direction.DRIVE_FORWARD, drive_distance, False
            elif blx <= end_left and end_right <= brx:  # stair is centered
                return Direction.DRIVE_FORWARD, 0, True
        elif bly > bry + border_offset:  # stair is right-skewed
            return Direction.ROTATE_RIGHT, rotation_angle, False
        elif bly < bry - border_offset:  # stair is left-skewed
            return Direction.ROTATE_LEFT, rotation_angle, False
        else:
            logging.error("Stair position is in an unexpected state.")

    def _calculate_intersections(self, lines_vertical, lines_horizontal):
        inters_left = []
        inters_right = []
        for ax1, ay1, ax2, ay2 in lines_horizontal:
            local_inters_left = []
            local_inters_right = []
            center_x = ax2 - ((ax2 - ax1) / 2)
            for bx1, by1, bx2, by2 in lines_vertical:
                ix, iy = self.image_processor.intersection((ax1, ay1), (ax2, ay2), (bx1, by1), (bx2, by2))
                if ix < center_x:
                    local_inters_left.append([ix, iy])
                else:
                    local_inters_right.append([ix, iy])

            # TODO: Simplify 'get minimum distance' to center with lambda
            nearest_inters_to_center_left = [0, 0]
            for i in local_inters_left:
                if (center_x - i[0]) < nearest_inters_to_center_left:
                    nearest_inters_to_center_left = i
            if nearest_inters_to_center_left != [0, 0]:
                inters_left.append(nearest_inters_to_center_left)

            nearest_inters_to_center_right = [0, 0]
            for i in local_inters_right:
                if (center_x - i[0]) < nearest_inters_to_center_right:
                    nearest_inters_to_center_right = i
            if nearest_inters_to_center_right != [0, 0]:
                inters_right.append(nearest_inters_to_center_right)
        return inters_left, inters_right

    def _calculate_stair_frame(self, intersections_left, intersections_right):
        tl = (0, 0)
        tr = (0, 0)
        bl = (0, 0)
        br = (0, 0)
        intersections_left.sort(key=lambda i: i[1], reverse=True)
        intersections_right.sort(key=lambda i: i[1], reverse=True)
        if len(intersections_left) > 0:
            bl = intersections_left[0]
            tl = intersections_left[-1]
        if len(intersections_right) > 0:
            br = intersections_right[0]
            tr = intersections_right[-1]
        return tl, tr, bl, br

    def _detect_handlebars(self, lines):
        lines = _remove_skew_lines(lines, int(self.conf["bars_lines_min_angle"]), int(self.conf["bars_lines_max_angle"]))
        lines.sort(key=lambda l: l[0], reverse=False)  # sort lines by x1 from left of the image to right
        lines = _remove_horizontally_close_lines(lines, int(self.conf["bars_lines_min_line_gap"]))
        return lines

    def _detect_steps(self, lines, img_height):
        lines = _remove_skew_lines(lines, int(self.conf["steps_lines_min_angle"]), int(self.conf["steps_lines_max_angle"]))
        lines.sort(key=lambda l: l[1], reverse=True)  # sort lines by x1 from left of the image to right
        lines = _remove_vertically_close_lines(lines, img_height, int(self.conf["steps_lines_min_line_gap"]))
        return lines
