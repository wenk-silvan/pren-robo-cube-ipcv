from __future__ import print_function
import math
import cv2
import numpy as np


def _pass(_):
    pass


def draw_lines(lines, img):
    for x1, y1, x2, y2 in lines:
        p1 = (x1, y1)
        p2 = (x2, y2)
        if not p1 or not p2:
            continue
        cv2.line(img, p1, p2, (255, 0, 0), 2)


def detect_lines_probabilistic(canny):
    detected = cv2.HoughLinesP(
        canny,
        rho=cv2.getTrackbarPos("Rho", "Hough"),
        theta=1 * np.pi / 180,
        threshold=cv2.getTrackbarPos("Thresh", "Hough"),
        minLineLength=cv2.getTrackbarPos("MinLineLength", "Hough"),
        maxLineGap=cv2.getTrackbarPos("MaxLineGap", "Hough")
    )
    return [[l[0][0], l[0][1], l[0][2], l[0][3]] for l in detected]


def detect_lines(canny):
    lines = []
    detected = cv2.HoughLines(
        canny,
        rho=cv2.getTrackbarPos("Rho", "Hough"),
        theta=1 * np.pi / 180,
        threshold=cv2.getTrackbarPos("Thresh", "Hough")
    )
    for line in detected:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * a)
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * a)
        lines.append([x1, y1, x2, y2])
    return lines


def remove_skew_lines(lines, min_angle, max_angle):
    lines_not_skew = []
    for x1, y1, x2, y2 in lines:
        angle = math.atan2(abs(y1 - y2), abs(x1 - x2)) * 180 / np.pi
        if min_angle <= angle <= max_angle:
            lines_not_skew.append([x1, y1, x2, y2])
    return lines_not_skew


def remove_close_lines(lines, img_height, min_line_gap):
    previous_y1 = img_height
    lines_not_close = []
    for x1, y1, x2, y2 in lines:
        if (previous_y1 - y1) >= min_line_gap:
            lines_not_close.append([x1, y1, x2, y2])
            previous_y1 = y1
    return lines_not_close


image = cv2.imread("../../images/stair/front_left/img029.jpg")
image = cv2.resize(image, (600, 400))
img_width = image.shape[1]
img_height = image.shape[0]

# min_angle = 0
# max_angle = 6
# rho = 1
# theta = 1 * np.pi / 180
# thresh = 125
# min_line_length = 10
# max_line_gap = 500
# min_line_gap = 30
# canny_thresh_1 = 44
# canny_thresh_2 = 183

min_angle = 40
max_angle = 90
rho = 1
theta = 1 * np.pi / 180
thresh = 100
min_line_length = 10
max_line_gap = 500
min_line_gap = 0
canny_thresh_1 = 44
canny_thresh_2 = 183

cv2.namedWindow("Hough")
cv2.createTrackbar("MinAngle", "Hough", min_angle, 90, _pass)
cv2.createTrackbar("MaxAngle", "Hough", max_angle, 90, _pass)
cv2.createTrackbar("Rho", "Hough", rho, 255, _pass)
cv2.createTrackbar("Thresh", "Hough", thresh, 255, _pass)
cv2.createTrackbar("MinLineLength", "Hough", min_line_length, img_width, _pass)
cv2.createTrackbar("MaxLineGap", "Hough", max_line_gap, img_height, _pass)
cv2.createTrackbar("MinLineGap", "Hough", min_line_gap, img_height, _pass)
cv2.createTrackbar("CannyThresh1", "Hough", canny_thresh_1, 255, _pass)
cv2.createTrackbar("CannyThresh2", "Hough", canny_thresh_2, 255, _pass)

while 1:
    img = image.copy()
    blurred = cv2.GaussianBlur(img, (5, 5), 0, 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)

    # ret, thresh = cv2.threshold(gray, cv2.getTrackbarPos("CannyThresh1", "Hough"), cv2.getTrackbarPos("CannyThresh2", "Hough"), cv2.THRESH_BINARY)
    # #thresh = cv2.bitwise_not(thresh)
    # cv2.imshow("Thresh", thresh)

    canny = cv2.Canny(gray, cv2.getTrackbarPos("CannyThresh1", "Hough"), cv2.getTrackbarPos("CannyThresh2", "Hough"), 3)
    cv2.imshow("Canny", canny)

    # contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # cv2.drawContours(img, contours, -1, (0, 255, 0), 2)

    lines = detect_lines_probabilistic(canny)
    lines = remove_skew_lines(lines, cv2.getTrackbarPos("MinAngle", "Hough"), cv2.getTrackbarPos("MaxAngle", "Hough"))
    lines.sort(key=lambda l: l[1], reverse=True)  # sort lines by y1 from bottom of the image to top
    lines = remove_close_lines(lines, img_height, cv2.getTrackbarPos("MinLineGap", "Hough"))
    draw_lines(lines, img)

    cv2.imshow("Hough", img)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:  # ESC
        break
