import cv2
import numpy as np
from matplotlib import pyplot as plt


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

    def transform_to_2d(self):
        tl, tr, bl, br = self.__find_edges()
        pts1 = np.float32(
            [list(tl),
             list(tr),
             list(bl),
             list(br)]
        )
        pts2 = np.float32(
            [[0, 0],
             [600, 0],
             [0, 600],
             [600, 600]]
        )

        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(self.image, matrix, (600, 600))

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


# plt.subplot(1, 2, 1),
# plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
# plt.title('Original Image')
#
# plt.subplot(1, 2, 2),
# plt.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
# plt.title('Result')
#
# plt.show()
# cv2.waitKey(0)
