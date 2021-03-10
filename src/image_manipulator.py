import cv2
import numpy as np
import matplotlib.pyplot as plt


class ImageManipulator:
    def __init__(self, image):
        self.image = image

    def find_edges(self):
        # TODO: Determine edges with OpenCV
        top_left = (320, 260)
        top_right = (950, 260)
        bottom_left = (5, 955)
        bottom_right = (1275, 955)
        return top_left, top_right, bottom_left, bottom_right

    def draw_circles(self):
        tl, tr, bl, br = self.find_edges()
        cv2.circle(self.image, tl, 5, (0, 0, 255), -1)
        cv2.circle(self.image, tr, 5, (0, 0, 255), -1)
        cv2.circle(self.image, bl, 5, (0, 0, 255), -1)
        cv2.circle(self.image, br, 5, (0, 0, 255), -1)
        cv2.imshow("Image", self.image)
        cv2.waitKey(0)

    def transform_to_2d(self):
        tl, tr, bl, br = self.find_edges()
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
