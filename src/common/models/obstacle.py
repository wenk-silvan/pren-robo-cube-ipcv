from src.common.models.point import Point


def midpoint(a: Point, b: Point):
    return Point((a.x + b.x) * 0.5, (a.y + b.y) * 0.5)


class Obstacle:
    def __init__(self, top_left: Point, bottom_right: Point):
        x, y = top_left.x, top_left.y
        width, height = abs(bottom_right.x - top_left.x), abs(bottom_right.y - top_left.y)

        self.top_left = Point(x, y)
        self.top_right = Point(x + width, y)
        self.top_center = midpoint(self.top_left, self.top_right)
        self.bottom_left = Point(x, y + height)
        self.bottom_right = Point(x + width, y + height)
        self.bottom_center = midpoint(self.bottom_left, self.bottom_right)
        self.left_center = midpoint(self.top_left, self.bottom_left)
        self.right_center = midpoint(self.top_right, self.bottom_right)
