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
HOUGH_LINES_OFFSET = 20
ROBOCUBE_WIDTH_MILLIMETER = 250
STAIR_WIDTH_MILLIMETER = 2000
MATRICE_CELL_SIZE_MILLIMETER = 10


def _draw(p1, p2, img):
    if img is None: return
    cv2.line(img, p1, p2, (255, 0, 0), 2)


def _draw_lines(lines, img, width):
    if lines is None:
        return
    y_values = []
    drawn = []

    for x in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[x]:
            if abs(y1 - y2) > 10:
                continue

            if len(y_values) == 0:
                p1 = (STAIR_WIDTH_OFFSET, y1)
                p2 = (width - STAIR_WIDTH_OFFSET, y2)
                _draw(p1=p1, p2=p2, img=img)
                y_values.append(y1)
                drawn.append(Line(p1, p2))

            has_neighbour = False
            for y in y_values:
                if len(y_values) > 0 and abs(y - y1) < 30:
                    has_neighbour = True
                    break

            if not has_neighbour:
                p1 = (STAIR_WIDTH_OFFSET, y1)
                p2 = (width - STAIR_WIDTH_OFFSET, y2)
                _draw(p1=p1, p2=p2, img=img)
                y_values.append(y1)
                drawn.append(Line(p1, p2))

    cv2.imshow("Result", img)
    cv2.waitKey(0)
    return drawn


class Pathfinder:
    def __init__(self, img):
        self.obstacles = []
        self.img = img
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
        canny = cv2.Canny(gray, 80, 240, 3)
        lines = cv2.HoughLinesP(
            canny,
            rho=1,
            theta=1 * np.pi / 180,
            threshold=140,
            minLineLength=90,
            maxLineGap=90
        )
        return _draw_lines(lines, self.img, self.img_width)

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
        lines.sort(key=attrgetter('p1y'), reverse=True)

        for line in lines:
            obs = [o for o in obstacles if
                   line.p1y - HOUGH_LINES_OFFSET <= o.bottom_center[1] <= line.p1y + HOUGH_LINES_OFFSET]
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

        position = self.stair_end_left
        matrice = stair.get_rows()
        combinations = list(itertools.product(*matrice))
        possible_positions = []
        for c in combinations:
            positions = []
            for i in range(stair.count()):
                if c[i][0] <= position <= c[i][1]:  # if current position is in area above
                    positions.append(position)
                elif position < c[i][0]:  # if current position is left to area above
                    if i == 0 or c[i][0] <= (
                            c[i - 1][1] - self.robocube_width):  # and current area allows to move right
                        position = c[i][0]
                        positions.append(position)
                elif c[i][1] < position:  # if current position is right to area above
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
