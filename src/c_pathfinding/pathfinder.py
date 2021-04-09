import numpy as np
import cv2
import itertools

from src.common.models.line import Line
from src.common.models.obstacle import Obstacle
from src.common.models.path import Path
from src.common.models.stair import Stair
from src.common.movement.direction import Direction


class Pathfinder:
    def __init__(self, img, configuration):
        self.conf = configuration
        self.obstacles = []
        self.img = img
        self.img_height = img.shape[0]
        self.img_width = img.shape[1]
        self.stair = Stair()
        self.stair_min_line_gap = int(self.conf["staircase_min_line_gap"])
        self.stair_width_offset = int(self.conf["staircase_width_offset"])
        self.stair_end_right = self.img_width - self.stair_width_offset
        self.stair_end_left = self.stair_width_offset
        self.pixel_per_mm = (self.img_width - self.stair_width_offset) / int(self.conf["staircase_width_millimeter"])
        self.robocube_width = int(self.pixel_per_mm * int(self.conf["robot_width_millimeter"]))

    def find_obstacles(self, cascade):
        scale_val = float(self.conf["obstacles_scale_val"])
        neighbours = int(self.conf["obstacles_neighbors"])
        min_height = int(self.conf["obstacles_min_height"])
        min_width = int(self.conf["obstacles_min_width"])

        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        obstacles = cascade.detectMultiScale(gray, scale_val, neighbours)
        for (x, y, w, h) in obstacles:
            if w < min_width or h < min_height:
                continue
            self.obstacles.append(Obstacle(x, y, w, h))
        return self.obstacles

    def find_hough_lines(self):
        gauss = cv2.GaussianBlur(self.img, (5, 5), 0, 0)
        gray = cv2.cvtColor(gauss, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray, int(self.conf["staircase_canny_thresh1"]), int(self.conf["staircase_canny_thresh2"]), 3)

        lines = cv2.HoughLinesP(
            canny,
            rho=int(self.conf["staircase_lines_rho"]),
            theta=1 * np.pi / 180,
            threshold=int(self.conf["staircase_lines_thresh"]),
            minLineLength=int(self.conf["staircase_lines_min_line_length"]),
            maxLineGap=self.img_height
        )

        lines = Pathfinder.remove_skew_lines(lines, int(self.conf["staircase_max_skewness"]))
        lines.sort(key=lambda l: l[1], reverse=True)  # sort lines by y1 from bottom of the image to top
        lines = Pathfinder.remove_close_lines(lines, self.img_height, self.stair_min_line_gap)
        return Pathfinder.draw_lines(lines, self.img)

    def convert_to_matrice(self, stair):
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
        if not isinstance(obstacles, list):
            print("Err: The provided object must be a list of Obstacle.")
            return
        stair = Stair()
        lines = self.find_hough_lines()
        Pathfinder.draw_obstacles(obstacles, self.img)
        cv2.imshow("Result", self.img)
        cv2.waitKey(0)

        distance_to_step = int(self.conf["obstacles_distance_to_step"])
        if lines:
            for line in lines:
                obs = [o for o in obstacles if
                       line.p1y - distance_to_step <= o.bottom_center[1] <= line.p1y + distance_to_step]
                obs.sort(key=lambda l: l.bottom_left[0], reverse=False)  # sort obstacles from left to right
                stair.add_row(obs)
        return stair

    def create_stair_passable_areas(self, stair_objects):
        if not isinstance(stair_objects, Stair):
            print("Err: The provided object is not of type Stair.")
            return
        stair_areas = Stair()
        for i in range(stair_objects.count()):
            row = stair_objects.get(i)
            areas = self.__get_x_coords_possible_areas(row)
            stair_areas.add_row(areas)
        return stair_areas

    def calculate_path(self, stair_areas):
        path = Path()
        possible_positions = self.__calculate_path_sequential(stair_areas)
        if len(possible_positions) == 0:
            print("Err: No passable path found.")
            return

        # TODO: Pick best instead of firstl
        current_pos = self.stair_end_left
        for pos in possible_positions[0]:
            distance_millimeter = abs(current_pos - pos) / self.pixel_per_mm
            if pos < current_pos:
                path.add_instruction(Direction.DRIVE_LEFT, distance_millimeter)
            else:
                path.add_instruction(Direction.DRIVE_RIGHT, distance_millimeter)
            current_pos = pos
        return path

    def __get_x_coords_possible_areas(self, obstacles_sorted_left_to_right):
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
            if (obstacle.bottom_left[0] - self.stair_end_left) > self.robocube_width:
                areas.append((self.stair_end_left, obstacle.bottom_left[0]))
            # and width to right end of row is bigger than Robo-Cube
            if (self.stair_end_right - obstacle.bottom_right[0]) > self.robocube_width:
                areas.append((obstacle.bottom_right[0], self.stair_end_right))
            return areas

        # if two obstacles
        if count == 2:
            obstacle1 = obstacles_sorted_left_to_right[0]
            obstacle2 = obstacles_sorted_left_to_right[1]

            # and width to left end of row of obstacle 1 is bigger than Robo-Cube
            if (obstacle1.bottom_left[0] - self.stair_end_left) > self.robocube_width:
                areas.append((self.stair_end_left, obstacle1.bottom_left[0]))

            # and width between obstacles is bigger than Robo-Cube
            if (obstacle2.bottom_left[0] - obstacle1.bottom_right[0]) > self.robocube_width:
                areas.append((obstacle1.bottom_right[0], obstacle2.bottom_left[0]))

            # and width to right end of row of obstacle 2 is bigger than Robo-Cube
            if (self.stair_end_right - obstacle2.bottom_right[0]) > self.robocube_width:
                areas.append((obstacle2.bottom_right[0], self.stair_end_right))
            return areas

        # if three obstacles
        if count == 3:
            obstacle1 = obstacles_sorted_left_to_right[0]
            obstacle2 = obstacles_sorted_left_to_right[1]
            obstacle3 = obstacles_sorted_left_to_right[2]

            # and width to left end of row of obstacle 1 is bigger than Robo-Cube
            if (obstacle1.bottom_left[0] - self.stair_end_left) > self.robocube_width:
                areas.append((self.stair_end_left, obstacle1.bottom_left[0]))

            # and width between obstacle 1 and 2 is bigger than Robo-Cube
            if (obstacle2.bottom_left[0] - obstacle1.bottom_right[0]) > self.robocube_width:
                areas.append((obstacle1.bottom_right[0], obstacle2.bottom_left[0]))

            # and width between obstacle 2 and 3 is bigger than Robo-Cube
            if (obstacle3.bottom_left[0] - obstacle2.bottom_right[0]) > self.robocube_width:
                areas.append((obstacle2.bottom_right[0], obstacle3.bottom_left[0]))

            # and width to right end of row of obstacle 2 is bigger than Robo-Cube
            if (self.stair_end_right - obstacle3.bottom_right[0]) > self.robocube_width:
                areas.append((obstacle3.bottom_right[0], self.stair_end_right))
            return areas

    def __calculate_path_sequential(self, stair):
        if not isinstance(stair, Stair):
            print("Err: The provided object is not of type Stair.")
            return

        matrice = stair.get_rows()
        combinations = list(itertools.product(*matrice))
        possible_positions = []
        for c in combinations:
            position = self.stair_end_left
            positions = []
            for i in range(stair.count()):
                if c[i][0] <= position and position + self.robocube_width <= c[i][1]:  # if current position is in area above
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
            if k == 27: # ESC
                break

    @staticmethod
    def draw_line(p1, p2, img, color):
        if img is None:
            return
        cv2.line(img, p1, p2, color, 2)

    @staticmethod
    def draw_lines(lines, img):
        drawn = []
        for x1, y1, x2, y2 in lines:
            p1 = (x1, y1)
            p2 = (x2, y2)
            if not p1 or not p2:
                continue
            Pathfinder.draw_line(p1=p1, p2=p2, img=img, color=(255, 0, 0))
            drawn.append(Line(p1, p2))
        return drawn

    @staticmethod
    def draw_obstacles(obstacles, img):
        for o in obstacles:
            Pathfinder.draw_line(o.top_left, o.top_right, img=img, color=(0, 255, 0))
            Pathfinder.draw_line(o.top_left, o.bottom_left, img=img, color=(0, 255, 0))
            Pathfinder.draw_line(o.bottom_left, o.bottom_right, img=img, color=(0, 255, 0))
            Pathfinder.draw_line(o.bottom_right, o.top_right, img=img, color=(0, 255, 0))

    @staticmethod
    def hough_lines_parameters_adjustment(img_width, img_height, canny, image, max_line_skewness,
                                          rho, thresh, min_line_length, max_line_gap):
        """TRACKBAR TO ADJUST HOUGHLINESP PARAMETERS"""
        cv2.namedWindow("Hough")
        cv2.createTrackbar("Rho", "Hough", rho, 255, Pathfinder._pass)
        cv2.createTrackbar("Thresh", "Hough", thresh, 255, Pathfinder._pass)
        cv2.createTrackbar("MinLineLength", "Hough", min_line_length, img_width, Pathfinder._pass)
        cv2.createTrackbar("MaxLineGap", "Hough", max_line_gap, img_height, Pathfinder._pass)

        while 1:
            img = image.copy()
            lines = cv2.HoughLinesP(
                canny,
                rho=cv2.getTrackbarPos("Rho", "Hough"),
                theta=1 * np.pi / 180,
                threshold=cv2.getTrackbarPos("Thresh", "Hough"),
                minLineLength=cv2.getTrackbarPos("MinLineLength", "Hough"),
                maxLineGap=cv2.getTrackbarPos("MaxLineGap", "Hough")
            )

            lines = Pathfinder.remove_skew_lines(lines, max_line_skewness)
            lines.sort(key=lambda l: l[1], reverse=True)  # sort lines by y1 from bottom of the image to top
            lines = Pathfinder.remove_close_lines(lines, img_height)
            lines = Pathfinder.draw_lines(lines, img)
            cv2.imshow("Hough", img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:  # ESC
                break

    @staticmethod
    def _pass(_):
        pass

    @staticmethod
    def remove_close_lines(lines, img_height, min_line_gap):
        previous_y1 = img_height + 50
        lines_not_close = []
        for x1, y1, x2, y2 in lines:
            if (previous_y1 - y1) >= min_line_gap:
                lines_not_close.append([x1, y1, x2, y2])
                previous_y1 = y1
        return lines_not_close

    @staticmethod
    def remove_skew_lines(lines, delta_pixel):
        lines_straight = []
        # TODO: Simplify with list comprehension
        # TODO: Use angle instead of delta in pixel
        for x in range(0, len(lines)):
            for x1, y1, x2, y2 in lines[x]:
                if abs(y1 - y2) < delta_pixel:
                    lines_straight.append([x1, y1, x2, y2])
        return lines_straight
