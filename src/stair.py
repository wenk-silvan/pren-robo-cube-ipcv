import numpy as np


class Stair:
    def __init__(self):
        self.rows = []

    def add_row(self, areas):
        self.rows.append(areas)

    def count(self):
        return len(self.rows)

    def get(self, i):
        if len(self.rows) >= i + 1:
            return self.rows[i]
        return None

    def get_rows(self):
        return list(self.rows)
