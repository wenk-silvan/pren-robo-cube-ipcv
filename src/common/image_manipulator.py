import cv2
import numpy as np
from matplotlib import pyplot as plt

from src.common.models.obstacle import Obstacle
from src.common.models.point import Point


class ImageManipulator:
    def __init__(self, image):
        self.image = image

    def enhance_stair_visibility(self):
        """This method aims to improve the visibility of the staircases using color thresholding.
        However since in competition there might be different reflections, this would not be reliable."""
        img_hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        cv2.waitKey(0)
        min = np.array([0, 0, 0])
        max = np.array([20, 255, 255])
        tmp1 = cv2.inRange(img_hsv, min, max)
        plt.imshow(tmp1, cmap='gray')
        plt.subplot(1, 2, 1)
        cv2.imshow("Result", img_hsv)
        cv2.waitKey(0)
        plt.subplot(1, 2, 2)
        cv2.imshow("Result", tmp1)
        cv2.waitKey(0)

    def transform_to_2d(self, dimensions):
        """
        Squeeze the image into a 2d image by removing it's perspective. Top, left and right coordinates are hardcoded.
        :return: new image.
        """
        tl, tr, bl, br = self.__find_edges()
        pts1 = np.float32(
            [list(tl),
             list(tr),
             list(bl),
             list(br)]
        )
        pts2 = np.float32(
            [[0, 0],
             [dimensions[0], 0],
             [0, dimensions[1]],
             [dimensions[0], dimensions[1]]]
        )

        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(self.image, matrix, dimensions), matrix

    def transform_obstacle_coordinates(self, matrix, obstacle: Obstacle):
        """
        Transform the coordinates of the given obstacle using a matrix from transform_to_2d(...)
        :param matrix:
        :param obstacle:
        :return: a new obstacle with the transformed coordinates
        """
        tlx, tly, tlz = matrix.dot([obstacle.top_left.x, obstacle.top_left.y, 1])
        brx, bry, brz = matrix.dot([obstacle.bottom_right.x, obstacle.bottom_right.y, 1])
        tl_normalized = Point(int(tlx / tlz), int(tly / tlz))
        br_normalized = Point(int(brx / brz), int(bry / brz))
        return Obstacle(tl_normalized, br_normalized)

    def __draw_circles(self):
        tl, tr, bl, br = self.__find_edges()
        cv2.circle(self.image, tl, 5, (0, 0, 255), -1)
        cv2.circle(self.image, tr, 5, (0, 0, 255), -1)
        cv2.circle(self.image, bl, 5, (0, 0, 255), -1)
        cv2.circle(self.image, br, 5, (0, 0, 255), -1)
        cv2.imshow("Image", self.image)
        cv2.waitKey(0)

    def __find_edges(self):
        # TODO: Determine edges with OpenCV
        top_left = (350, 220)
        top_right = (920, 220)
        bottom_left = (0, self.image.shape[0])
        bottom_right = (self.image.shape[1], self.image.shape[0])
        return top_left, top_right, bottom_left, bottom_right
