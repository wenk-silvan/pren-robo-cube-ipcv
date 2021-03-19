import numpy as np
import cv2
import itertools
from line import Line
from stair import Stair
from obstacle import Obstacle
from operator import attrgetter
from path import Path
from direction import Direction

PINK = (255, 0, 255)
FONT_COLOR = (255, 0, 0)
PIVOT_WIDTH_MM = 160
OBJECT_TEXT = "Ziegel"
STAIR_WIDTH_OFFSET = 20
HOUGH_LINES_OFFSET = 50
ROBOCUBE_WIDTH_MILLIMETER = 250
STAIR_WIDTH_MILLIMETER = 2000
MATRICE_CELL_SIZE_MILLIMETER = 10
MIN_LINE_GAP = 70


def _canny_parameters_adjustment(gray):
    """TRACKBAR TO ADJUST HOUGHLINESP PARAMETERS"""
    cv2.namedWindow("Canny")
    cv2.createTrackbar("Thresh 1", "Canny", 44, 255, _pass)
    cv2.createTrackbar("Thresh 2", "Canny", 138, 255, _pass)

    while 1:
        t1 = cv2.getTrackbarPos("Thresh 1", "Canny")
        t2 = cv2.getTrackbarPos("Thresh 2", "Canny")
        canny = cv2.Canny(image=gray, threshold1=t1, threshold2=t2, apertureSize=3)
        cv2.imshow("Canny", canny)
        k = cv2.waitKey(1) & 0xFF
        if k == 27: # ESC
            break


def _draw_line(p1, p2, img, color):
    if img is None:
        return
    cv2.line(img, p1, p2, color, 2)


def _draw_lines(lines, img):
    drawn = []
    img_height, img_width, _ = img.shape
    for x1, y1, x2, y2 in lines:
        p1 = (x1, y1)
        p2 = (x2, y2)
        _draw_line(p1=p1, p2=p2, img=img, color=(255, 0, 0))
        drawn.append(Line(p1, p2))
    return drawn


def _draw_obstacles(obstacles, img):
    for o in obstacles:
        _draw_line(o.top_left, o.top_right, img=img, color=(0, 255, 0))
        _draw_line(o.top_left, o.bottom_left, img=img, color=(0, 255, 0))
        _draw_line(o.bottom_left, o.bottom_right, img=img, color=(0, 255, 0))
        _draw_line(o.bottom_right, o.top_right, img=img, color=(0, 255, 0))


def _hough_lines_parameters_adjustment(img_width, img_height, canny, image):
    """TRACKBAR TO ADJUST HOUGHLINESP PARAMETERS"""
    cv2.namedWindow("Hough")
    cv2.createTrackbar("Rho", "Hough", 1, 255, _pass)
    cv2.createTrackbar("Thresh", "Hough", 50, 255, _pass)
    cv2.createTrackbar("MinLineLength", "Hough", 138, img_width, _pass)
    cv2.createTrackbar("MaxLineGap", "Hough", 200, img_height, _pass)

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

        lines = _remove_skew_lines(lines, 10)
        lines.sort(key=lambda l: l[1], reverse=True)  # sort lines by y1 from bottom of the image to top
        lines = _remove_close_lines(lines, img_height)
        lines = _draw_lines(lines, img)
        cv2.imshow("Hough", img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:  # ESC
            break


def _pass(_):
    pass


def _remove_close_lines(lines, img_height):
    previous_y1 = img_height
    lines_not_close = []
    for x1, y1, x2, y2 in lines:
        if (previous_y1 - y1) >= MIN_LINE_GAP:
            lines_not_close.append([x1, y1, x2, y2])
            previous_y1 = y1
    return lines_not_close


def _remove_skew_lines(lines, delta_pixel):
    lines_straight = []
    # TODO: Simplify, maybe use list comprehension
    for x in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[x]:
            if abs(y1 - y2) < delta_pixel:
                lines_straight.append([x1, y1, x2, y2])
    return lines_straight


class Pathfinder:
    def __init__(self, img):
        self.obstacles = []
        self.img = img
        self.img_height = img.shape[0]
        self.img_width = img.shape[1]
        self.stair = Stair()
        self.pixel_per_mm = (self.img_width - HOUGH_LINES_OFFSET) / STAIR_WIDTH_MILLIMETER
        self.robocube_width = int(self.pixel_per_mm * ROBOCUBE_WIDTH_MILLIMETER)
        self.matrice_cell_size = self.pixel_per_mm * MATRICE_CELL_SIZE_MILLIMETER
        self.stair_end_right = self.img_width - STAIR_WIDTH_OFFSET
        self.stair_end_left = STAIR_WIDTH_OFFSET

    def find_obstacles(self, cascade, min_area, scale_val, neighbours):
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        obstacles = cascade.detectMultiScale(gray, scale_val, neighbours)
        for (x, y, w, h) in obstacles:
            if w * h < min_area:
                continue
            self.obstacles.append(Obstacle(x, y, w, h))
        return self.obstacles

    def find_hough_lines(self):
        gauss = cv2.GaussianBlur(self.img, (5, 5), 0, 0)
        gray = cv2.cvtColor(gauss, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(gray, 44, 138, 3)
        lines = cv2.HoughLinesP(
            canny,
            rho=3,
            theta=1 * np.pi / 180,
            threshold=127,
            minLineLength=(3/4) * self.img_width,
            maxLineGap=self.img_height
        )

        lines = _remove_skew_lines(lines, 10)
        lines.sort(key=lambda l: l[1], reverse=True)  # sort lines by y1 from bottom of the image to top
        lines = _remove_close_lines(lines, self.img_height)
        return _draw_lines(lines, self.img)

    # maybe deprecated
    def convert_to_matrice(self, stair):
        if not isinstance(stair, Stair):
            print("Err: The provided object is not of type Stair.")
            return
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
                cursor += self.matrice_cell_size
            matrice.append(cells)
        return matrice

    def create_stair_with_objects(self, obstacles):
        if not isinstance(obstacles, list):
            print("Err: The provided object must be a list of Obstacle.")
            return
        stair = Stair()
        lines = self.find_hough_lines()
        _draw_obstacles(obstacles, self.img)
        cv2.imshow("Result", self.img)
        cv2.waitKey(0)

        if lines:
            for line in lines:
                obs = [o for o in obstacles if
                       line.p1y - HOUGH_LINES_OFFSET <= o.bottom_center[1] <= line.p1y + HOUGH_LINES_OFFSET]
                obs.sort(key=lambda l: l.bottom_left[0], reverse=False) # sort obstacles from left to right
                stair.add_row(obs)
        return stair

    def create_stair_passable_areas(self, stair_objects):
        if not isinstance(stair_objects, Stair):
            print("Err: The provided object is not of type Stair.")
            return
        stair_areas = Stair()
        for i in range(stair_objects.count()):
            row = stair_objects.get(i)
            areas = self._get_x_coords_possible_areas(row)
            stair_areas.add_row(areas)
        return stair_areas

    def calculate_path(self, stair_areas):
        path = Path()
        possible_positions = self._calculate_path_sequential(stair_areas)
        if len(possible_positions) == 0:
            print("Err: No passable path found.")
            return

        # TODO: Pick best instead of firstl
        current_pos = self.stair_end_left
        for pos in possible_positions[0]:
            distance_millimeter = abs(current_pos - pos) / self.pixel_per_mm
            if pos < current_pos:
                path.add_instruction(Direction.LEFT, distance_millimeter)
            else:
                path.add_instruction(Direction.RIGHT, distance_millimeter)
            current_pos = pos
        return path

    def _get_x_coords_possible_areas(self, obstacles_sorted_left_to_right):
        # TODO: Improve hardcoded count of obstacles per row
        areas = []  # tuples with left and right x coordinate
        count = len(obstacles_sorted_left_to_right)

        # If no obstacles, add whole row
        if count == 0:
            areas.append((STAIR_WIDTH_OFFSET, self.stair_end_right))
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

    def _calculate_path_sequential(self, stair):
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
