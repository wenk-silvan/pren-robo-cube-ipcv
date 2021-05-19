import numpy as np
import cv2
import itertools

from src.common.models.line import Line
from src.common.models.path import Path
from src.common.models.point import Point
from src.common.models.stair import Stair
from src.common.movement.direction import Direction


class Pathfinder:
    def __init__(self, img, conf):
        self.obstacles = []
        self.img = img
        self.img_height = img.shape[0]
        self.img_width = img.shape[1]
        self.stair = Stair()

        self.steps_canny_thresh1 = int(conf["steps_canny_thresh1"])
        self.steps_canny_thresh2 = int(conf["steps_canny_thresh2"])
        self.steps_lines_rho = int(conf["steps_lines_rho"])
        self.steps_lines_thresh = int(conf["steps_lines_thresh"])
        self.steps_lines_min_line_length = int(conf["steps_lines_min_line_length"])
        self.steps_max_angle = int(conf["steps_max_angle"])
        self.stair_min_line_gap = int(conf["steps_min_line_gap"])
        self.stair_min_line_gap_decrease = int(conf["steps_min_line_gap_decrease"])
        self.stair_width_offset = int(conf["steps_width_offset"])
        self.obstacles_distance_to_step = int(conf["obstacles_distance_to_step"])

        self.stair_end_right = self.img_width - self.stair_width_offset
        self.stair_end_left = self.stair_width_offset
        self.pixel_per_mm = (self.img_width - self.stair_width_offset) / int(conf["steps_width_millimeter"])
        self.robocube_width = int(self.pixel_per_mm * int(conf["robot_width_millimeter"]))

    def detect_steps(self):
        """
        Detect the steps by applying image filters and hough transformation.
        :return: Line[] -> if the image is good enough, the coordinates of the steps.
        """
        gauss = cv2.GaussianBlur(self.img, (5, 5), 0, 0)
        gray = cv2.cvtColor(gauss, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray, self.steps_canny_thresh1, self.steps_canny_thresh2, 3)

        # UNCOMMENT TO ADJUST PARAMETERS
        # self.hough_lines_parameters_adjustment(
        #     self.img_width, self.img_height, canny,
        #     self.img, self.steps_lines_rho, self.steps_lines_thresh, self.steps_lines_min_line_length,
        #     self.img_height, self.stair_min_line_gap, self.stair_min_line_gap_decrease, self.steps_max_angle
        # )

        detected = cv2.HoughLinesP(
            canny,
            rho=self.steps_lines_rho,
            theta=1 * np.pi / 180,
            threshold=self.steps_lines_thresh,
            minLineLength=self.steps_lines_min_line_length,
            maxLineGap=self.img_height
        )
        lines = [Line(Point(l[0][0], l[0][1]), Point(l[0][2], l[0][3])) for l in detected]
        lines = self._remove_skew_lines(lines, 0, self.steps_max_angle)
        lines.sort(key=lambda l: l.p1.y, reverse=True)  # sort lines by y1 from bottom to top
        lines = self._remove_vertically_close_lines(lines, self.img_height, self.stair_min_line_gap,
                                                    self.stair_min_line_gap_decrease)

        # UNCOMMENT TO DRAW LINES ON IMAGE
        # Pathfinder.draw_lines(lines, self.img)
        return lines

    def convert_to_matrice(self, stair):
        """
        Deprecated
        :param stair:
        :return:
        """
        if not isinstance(stair, Stair):
            print("Err: The provided object is not of type Stair.")
            return

        matrice_cell_size_millimeter = 10
        matrice_cell_size = self.pixel_per_mm * matrice_cell_size_millimeter
        matrice = []
        for i in range(stair.count()):
            cells = []
            cursor = self.stair_end_left
            row = stair.get(i)
            while cursor < self.stair_end_right:
                if any(area[0] <= cursor <= area[1] for area in row):
                    cells.append(1)
                else:
                    cells.append(0)
                cursor += matrice_cell_size
            matrice.append(cells)
        return matrice

    def create_stair_with_objects(self, obstacles):
        """
        Create Stair by detecting the steps in the image and combine with the given obstacle coordinates.
        :return: Stair object with obstacles as areas.
        """
        if not isinstance(obstacles, list):
            print("Err: The provided object must be a list of Obstacle.")
            return
        stair = Stair()
        lines = self.detect_steps()
        if lines:
            for line in lines:
                obs = [o for o in obstacles if
                       line.p1.y - self.obstacles_distance_to_step <= o.bottom_center.y <= line.p1.y + self.obstacles_distance_to_step]
                obs.sort(key=lambda l: l.bottom_left.x, reverse=False)  # sort obstacles from left to right
                stair.add_row(obs)
        return stair

    def create_stair_passable_areas(self, stair_objects: Stair):
        """
        Create new Stair by calculating the free spaces of the Stair with the obstacles.
        :param stair_objects: Stair object with obstacles as areas.
        :return: Stair object with free spaces as areas.
        """
        stair_areas = Stair()
        for i in range(stair_objects.count()):
            row = stair_objects.get(i)
            areas = self._get_x_coords_possible_areas(row)
            stair_areas.add_row(areas)
        return stair_areas

    def calculate_path(self, stair_areas: Stair):
        """
        Calculate all possible paths to clear the stair.
        :param stair_areas: Stair with free spaces as areas.
        :return: Path[]
        """
        possible_positions = self._calculate_path_sequential(stair_areas)
        if len(possible_positions) == 0:
            print("Err: No passable path found.")
            return

        paths = []
        for positions in possible_positions:
            current_pos = self.stair_end_right - (self.stair_end_right - self.stair_end_left) / 2

            path = Path()
            for pos in positions:
                distance_millimeter = abs(current_pos - pos) / self.pixel_per_mm
                if pos < current_pos:
                    path.add_instruction(Direction.DRIVE_LEFT, distance_millimeter)
                else:
                    path.add_instruction(Direction.DRIVE_RIGHT, distance_millimeter)
                current_pos = pos
            paths.append(path)
        return paths

    def _get_x_coords_possible_areas(self, obstacles_sorted_left_to_right):
        # TODO: Improve hardcoded count of obstacles per row
        areas = []  # tuples with left and right x coordinate
        count = len(obstacles_sorted_left_to_right)

        # If no obstacles, add whole row
        if count == 0:
            areas.append((self.stair_end_left, self.stair_end_right))
            return areas

        # if one obstacle
        if count == 1:
            obstacle = obstacles_sorted_left_to_right[0]
            # and width to left end of row is bigger than Robo-Cube
            if (obstacle.bottom_left.x - self.stair_end_left) > self.robocube_width:
                areas.append((self.stair_end_left, obstacle.bottom_left.x))
            # and width to right end of row is bigger than Robo-Cube
            if (self.stair_end_right - obstacle.bottom_right.x) > self.robocube_width:
                areas.append((obstacle.bottom_right.x, self.stair_end_right))
            return areas

        # if two obstacles
        if count == 2:
            obstacle1 = obstacles_sorted_left_to_right[0]
            obstacle2 = obstacles_sorted_left_to_right[1]

            # and width to left end of row of obstacle 1 is bigger than Robo-Cube
            if (obstacle1.bottom_left.x - self.stair_end_left) > self.robocube_width:
                areas.append((self.stair_end_left, obstacle1.bottom_left.x))

            # and width between obstacles is bigger than Robo-Cube
            if (obstacle2.bottom_left.x - obstacle1.bottom_right.x) > self.robocube_width:
                areas.append((obstacle1.bottom_right.x, obstacle2.bottom_left.x))

            # and width to right end of row of obstacle 2 is bigger than Robo-Cube
            if (self.stair_end_right - obstacle2.bottom_right.x) > self.robocube_width:
                areas.append((obstacle2.bottom_right.x, self.stair_end_right))
            return areas

        # if three obstacles
        if count == 3:
            obstacle1 = obstacles_sorted_left_to_right[0]
            obstacle2 = obstacles_sorted_left_to_right[1]
            obstacle3 = obstacles_sorted_left_to_right[2]

            # and width to left end of row of obstacle 1 is bigger than Robo-Cube
            if (obstacle1.bottom_left.x - self.stair_end_left) > self.robocube_width:
                areas.append((self.stair_end_left, obstacle1.bottom_left.x))

            # and width between obstacle 1 and 2 is bigger than Robo-Cube
            if (obstacle2.bottom_left.x - obstacle1.bottom_right.x) > self.robocube_width:
                areas.append((obstacle1.bottom_right.x, obstacle2.bottom_left.x))

            # and width between obstacle 2 and 3 is bigger than Robo-Cube
            if (obstacle3.bottom_left.x - obstacle2.bottom_right.x) > self.robocube_width:
                areas.append((obstacle2.bottom_right.x, obstacle3.bottom_left.x))

            # and width to right end of row of obstacle 2 is bigger than Robo-Cube
            if (self.stair_end_right - obstacle3.bottom_right.x) > self.robocube_width:
                areas.append((obstacle3.bottom_right.x, self.stair_end_right))
            return areas

    def _calculate_path_sequential(self, stair: Stair):
        matrice = stair.get_rows()
        combinations = list(itertools.product(*matrice))
        possible_positions = []
        for c in combinations:
            position = self.stair_end_left
            positions = []
            for i in range(stair.count()):
                # if current position is in area above
                if c[i][0] <= position and position + self.robocube_width <= c[i][1]:
                    positions.append(position)
                elif position < c[i][0]:  # if current position is left to area above
                    if i == 0 or c[i][0] <= (
                            c[i - 1][1] - self.robocube_width):  # and current area allows to move right
                        position = c[i][0]
                        positions.append(position)
                elif c[i][1] < position + self.robocube_width:  # if current position is right to area above
                    if i == 0:
                        position = c[i][0]
                        positions.append(position)
                    elif c[i][1] >= (c[i - 1][0] + self.robocube_width):  # and current area allows to move left
                        position = c[i - 1][0]
                        positions.append(position)
            if len(positions) == stair.count():
                possible_positions.append(positions)
        print(possible_positions)
        return possible_positions

    @staticmethod
    def canny_parameters_adjustment(gray, thresh1, thresh2):
        """TRACKBAR TO ADJUST HOUGHLINESP PARAMETERS"""
        cv2.namedWindow("Canny")
        cv2.createTrackbar("Thresh 1", "Canny", thresh1, 255, Pathfinder._pass)
        cv2.createTrackbar("Thresh 2", "Canny", thresh2, 255, Pathfinder._pass)

        while 1:
            t1 = cv2.getTrackbarPos("Thresh 1", "Canny")
            t2 = cv2.getTrackbarPos("Thresh 2", "Canny")
            canny = cv2.Canny(image=gray, threshold1=t1, threshold2=t2, apertureSize=3)
            cv2.imshow("Canny", canny)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:  # ESC
                break

    @staticmethod
    def determine_best_path(paths):
        """
        Get Path which counts the most instructions where the distance is 0.
        :param paths: Path[] - Possible paths to clear the stair.
        :return: Path - The fastest path.
        """
        shortest = min(paths, key=lambda p: len(list(filter(lambda i: i.distance > 0, p.instructions))))
        return shortest

    @staticmethod
    def draw_line(p1, p2, img, color):
        if img is None:
            return
        cv2.line(img, (p1.x, p1.y), (p2.x, p2.y), color, 2)

    @staticmethod
    def draw_lines(lines, img):
        [Pathfinder.draw_line(p1=l.p1, p2=l.p2, img=img, color=(255, 0, 0)) for l in lines]

    @staticmethod
    def hough_lines_parameters_adjustment(img_width, img_height, canny, image,
                                          rho, thresh, min_line_length, max_line_gap, min_line_gap,
                                          min_gap_decrease, max_angle):
        """TRACKBAR TO ADJUST HOUGHLINESP PARAMETERS"""
        cv2.namedWindow("Hough")
        cv2.createTrackbar("Rho", "Hough", rho, 255, Pathfinder._pass)
        cv2.createTrackbar("Thresh", "Hough", thresh, 255, Pathfinder._pass)
        cv2.createTrackbar("MinLineLength", "Hough", min_line_length, img_width, Pathfinder._pass)
        cv2.createTrackbar("MaxLineGap", "Hough", max_line_gap, img_height, Pathfinder._pass)
        cv2.createTrackbar("MinLineGap", "Hough", min_line_gap, img_height, Pathfinder._pass)
        cv2.createTrackbar("MaxAngle", "Hough", max_angle, 90, Pathfinder._pass)
        cv2.createTrackbar("GapDecrease", "Hough", min_gap_decrease, 50, Pathfinder._pass)

        while 1:
            img = image.copy()
            detected = cv2.HoughLinesP(
                canny,
                rho=cv2.getTrackbarPos("Rho", "Hough"),
                theta=1 * np.pi / 180,
                threshold=cv2.getTrackbarPos("Thresh", "Hough"),
                minLineLength=cv2.getTrackbarPos("MinLineLength", "Hough"),
                maxLineGap=cv2.getTrackbarPos("MaxLineGap", "Hough")
            )
            lines = [Line(Point(l[0][0], l[0][1]), Point(l[0][2], l[0][3])) for l in detected]
            lines = Pathfinder._remove_skew_lines(lines, 0, cv2.getTrackbarPos("MaxAngle", "Hough"))
            lines.sort(key=lambda l: l.p1.y, reverse=True)  # sort lines by y1 from bottom to top
            lines = Pathfinder._remove_vertically_close_lines(lines, img_height,
                                                              cv2.getTrackbarPos("MinLineGap", "Hough"),
                                                              cv2.getTrackbarPos("GapDecrease", "Hough"))
            Pathfinder.draw_lines(lines, img)
            cv2.imshow("Hough", img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:  # ESC
                break

    @staticmethod
    def _pass(_):
        pass

    @staticmethod
    def _remove_skew_lines(lines, min_angle, max_angle):
        return [l for l in lines
                if min_angle <= np.math.atan2(abs(l.p1.y - l.p2.y), abs(l.p1.x - l.p2.x)) * 180 / np.pi <= max_angle]

    @staticmethod
    def _remove_vertically_close_lines(lines, img_height, min_line_gap, min_gap_decrease_per_step):
        gap = min_line_gap
        previous_y1 = img_height + min_line_gap
        lines_not_close = []
        for l in lines:
            if (previous_y1 - l.p1.y) >= gap:
                lines_not_close.append(l)
                previous_y1 = l.p1.y
                gap -= min_gap_decrease_per_step
        return lines_not_close
