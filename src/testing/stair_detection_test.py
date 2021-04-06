from __future__ import print_function
import math
from configparser import ConfigParser

import cv2
import numpy as np

from src.b_find_stair_center.image_processing import ImageProcessing
from src.b_find_stair_center.stair_detection import StairDetection
from src.camera.camera import Camera


def _pass(_):
    pass


def draw_lines(lines, img, color):
    for x1, y1, x2, y2 in lines:
        p1 = (x1, y1)
        p2 = (x2, y2)
        if not p1 or not p2:
            continue
        cv2.line(img, p1, p2, color, 2)


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


def detect_lines_probabilistic(image, rho, threshold, min_line_length, max_line_gap, canny1, canny2):
    blurred = cv2.GaussianBlur(image, (5, 5), 0, 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(image=gray, threshold1=canny1, threshold2=canny2, apertureSize=3)
    detected = cv2.HoughLinesP(
        canny,
        rho=rho,
        theta=1 * np.pi / 180,
        threshold=threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap
    )
    return [[l[0][0], l[0][1], l[0][2], l[0][3]] for l in detected], canny


def _detect_handlebars(lines, min_angle, max_angle, min_line_gap):
    lines = _remove_skew_lines(lines, min_angle, max_angle)
    lines.sort(key=lambda l: l[0], reverse=False)  # sort lines by x1 from left of the image to right
    lines = _remove_horizontally_close_lines(lines, min_line_gap)
    return lines


def _detect_steps(lines, img_height, min_angle, max_angle, min_line_gap):
    lines = _remove_skew_lines(lines, min_angle, max_angle)
    lines.sort(key=lambda l: l[1], reverse=True)  # sort lines by x1 from left of the image to right
    lines = _remove_vertically_close_lines(lines, img_height, min_line_gap)
    return lines


def _remove_skew_lines(lines, min_angle, max_angle):
    return [[x1, y1, x2, y2] for x1, y1, x2, y2 in lines
            if min_angle <= np.math.atan2(abs(y1 - y2), abs(x1 - x2)) * 180 / np.pi <= max_angle]


def _remove_horizontally_close_lines(lines, min_line_gap):
    previous_x1 = 0
    lines_not_close = []
    for x1, y1, x2, y2 in lines:
        if (x1 - previous_x1) >= min_line_gap:
            lines_not_close.append([x1, y1, x2, y2])
            previous_x1 = x1
    return lines_not_close


def _remove_vertically_close_lines(lines, img_height, min_line_gap):
    previous_y1 = img_height
    lines_not_close = []
    for x1, y1, x2, y2 in lines:
        if (previous_y1 - y1) >= min_line_gap:
            lines_not_close.append([x1, y1, x2, y2])
            previous_y1 = y1
    return lines_not_close


config_object = ConfigParser()
config_object.read("../../resources/config.ini")
conf = config_object["B_FIND_STAIR_CENTER"]
image = cv2.imread(conf["img_2_path"])
# image = cv2.resize(image, (1000, 750))
stair = StairDetection(conf, ImageProcessing(conf), Camera(conf))

steps_lines_rho = conf["steps_lines_rho"]
steps_lines_threshold = conf["steps_lines_threshold"]
steps_lines_min_line_length = conf["steps_lines_min_line_length"]
steps_lines_min_line_gap = conf["steps_lines_min_line_gap"]
steps_lines_max_line_gap = conf["steps_lines_max_line_gap"]
steps_lines_min_angle = conf["steps_lines_min_angle"]
steps_lines_max_angle = conf["steps_lines_max_angle"]
steps_canny_thresh_1 = conf["steps_canny_thresh_1"]
steps_canny_thresh_2 = conf["steps_canny_thresh_2"]

bars_lines_rho = conf["bars_lines_rho"]
bars_lines_threshold = conf["bars_lines_threshold"]
bars_lines_min_line_length = conf["bars_lines_min_line_length"]
bars_lines_min_line_gap = conf["bars_lines_min_line_gap"]
bars_lines_max_line_gap = conf["bars_lines_max_line_gap"]
bars_lines_min_angle = conf["bars_lines_min_angle"]
bars_lines_max_angle = conf["bars_lines_max_angle"]
bars_canny_thresh_1 = conf["bars_canny_thresh_1"]
bars_canny_thresh_2 = conf["bars_canny_thresh_2"]

theta = 1 * np.pi / 180

cv2.namedWindow("Steps_Control")
cv2.createTrackbar("rho", "Steps_Control", int(steps_lines_rho), 255, _pass)
cv2.createTrackbar("threshold", "Steps_Control", int(steps_lines_threshold), 255, _pass)
cv2.createTrackbar("min_line_length", "Steps_Control", int(steps_lines_min_line_length), image.shape[1], _pass)
cv2.createTrackbar("min_line_gap", "Steps_Control", int(steps_lines_min_line_gap), image.shape[0], _pass)
cv2.createTrackbar("max_line_gap", "Steps_Control", int(steps_lines_max_line_gap), image.shape[0], _pass)
cv2.createTrackbar("min_angle", "Steps_Control", int(steps_lines_min_angle), 90, _pass)
cv2.createTrackbar("max_angle", "Steps_Control", int(steps_lines_max_angle), 90, _pass)
cv2.createTrackbar("canny_1", "Steps_Control", int(steps_canny_thresh_1), 255, _pass)
cv2.createTrackbar("canny_2", "Steps_Control", int(steps_canny_thresh_2), 255, _pass)

cv2.namedWindow("Bars_Control")
cv2.createTrackbar("rho", "Bars_Control", int(bars_lines_rho), 255, _pass)
cv2.createTrackbar("threshold", "Bars_Control", int(bars_lines_threshold), 255, _pass)
cv2.createTrackbar("min_line_length", "Bars_Control", int(bars_lines_min_line_length), image.shape[1], _pass)
cv2.createTrackbar("min_line_gap", "Bars_Control", int(bars_lines_min_line_gap), image.shape[0], _pass)
cv2.createTrackbar("max_line_gap", "Bars_Control", int(bars_lines_max_line_gap), image.shape[0], _pass)
cv2.createTrackbar("min_angle", "Bars_Control", int(bars_lines_min_angle), 90, _pass)
cv2.createTrackbar("max_angle", "Bars_Control", int(bars_lines_max_angle), 90, _pass)
cv2.createTrackbar("canny_1", "Bars_Control", int(bars_canny_thresh_1), 255, _pass)
cv2.createTrackbar("canny_2", "Bars_Control", int(bars_canny_thresh_2), 255, _pass)

while 1:
    img = image.copy()

    lines_horizontal, img_canny = detect_lines_probabilistic(
        img,
        cv2.getTrackbarPos("rho", "Steps_Control"),
        cv2.getTrackbarPos("threshold", "Steps_Control"),
        cv2.getTrackbarPos("min_line_length", "Steps_Control"),
        cv2.getTrackbarPos("max_line_gap", "Steps_Control"),
        cv2.getTrackbarPos("canny_1", "Steps_Control"),
        cv2.getTrackbarPos("canny_2", "Steps_Control")
    )
    lines_horizontal = _detect_steps(
        lines_horizontal,
        img.shape[0],
        cv2.getTrackbarPos("min_angle", "Steps_Control"),
        cv2.getTrackbarPos("max_angle", "Steps_Control"),
        cv2.getTrackbarPos("min_line_gap", "Steps_Control"))

    lines_vertical, _ = detect_lines_probabilistic(
        img,
        cv2.getTrackbarPos("rho", "Bars_Control"),
        cv2.getTrackbarPos("threshold", "Bars_Control"),
        cv2.getTrackbarPos("min_line_length", "Bars_Control"),
        cv2.getTrackbarPos("max_line_gap", "Bars_Control"),
        cv2.getTrackbarPos("canny_1", "Bars_Control"),
        cv2.getTrackbarPos("canny_2", "Bars_Control")
    )
    lines_vertical = _detect_handlebars(
        lines_vertical,
        cv2.getTrackbarPos("min_angle", "Bars_Control"),
        cv2.getTrackbarPos("max_angle", "Bars_Control"),
        cv2.getTrackbarPos("min_line_gap", "Bars_Control"))

    draw_lines(lines_horizontal, img, (255, 0, 0))
    draw_lines(lines_vertical, img, (0, 255, 0))
    cv2.imshow("Canny", img_canny)
    cv2.imshow("Stair", img)

    # contours, hierarchy = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # cv2.drawContours(img, contours, -1, (0, 255, 0), 2)

    k = cv2.waitKey(1) & 0xFF
    if k == 27:  # ESC
        break
