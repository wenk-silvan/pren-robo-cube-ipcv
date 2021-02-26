def midpoint(a, b):
    return (a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5


class Obstacle:
    def __init__(self, x, y, width, height):
        self.top_left = (x, y)
        self.top_right = (x + width, y)
        self.top_center = midpoint(self.top_left, self.top_right)
        self.bottom_left = (x, y + height)
        self.bottom_right = (x + width, y + height)
        self.bottom_center = midpoint(self.bottom_left, self.bottom_right)
        self.left_center = midpoint(self.top_left, self.bottom_left)
        self.right_center = midpoint(self.top_right, self.bottom_right)
