import os
import cv2


def generate_negative_description_file():
    with open('images_labeled/negative/hammer.txt', 'w') as f:
        for filename in os.listdir('./images/negative/hammer_small'):
            f.write('images/negative/hammer_small/' + filename + '\n')


def detect_and_display_object(img, gray, cascades, object_names, color):
    counter = 0
    o = None

    scale_val = 1.05 + (cv2.getTrackbarPos("Scale", "Result") / 1000)
    neighbours = cv2.getTrackbarPos("Neighbours", "Result")
    for c in cascades:
        objects = c.detectMultiScale(gray, scale_val, neighbours)
        for (x, y, w, h) in objects:
            area = w * h
            min_area = cv2.getTrackbarPos("Min Area", "Result")
            if area > min_area:
                o = object_names[cascades.index(c)]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 3)
                cv2.putText(img, o, (x, y - 5), cv2.CASCADE_FIND_BIGGEST_OBJECT, 1, color, 2)
                counter += 1

    return counter, o


def empty(a):
    pass


def create_trackbar(width, height):
    cv2.namedWindow("Result")
    cv2.resizeWindow("Result", width, height)
    cv2.createTrackbar("Scale", "Result", 200, 1000, empty)
    cv2.createTrackbar("Neighbours", "Result", 6, 50, empty)
    cv2.createTrackbar("Min Area", "Result", 400, 100000, empty)
    cv2.createTrackbar("Brightness", "Result", 100, 255, empty)
    cv2.createTrackbar("BinaryThreshold", "Result", 123, 255, empty)


def add_trackbar_hough():
    cv2.createTrackbar("Rho", "Result", 1, 10, empty)
    cv2.createTrackbar("Theta", "Result", 1, 10, empty)
    cv2.createTrackbar("Threshold", "Result", 1, 300, empty)
    cv2.createTrackbar("minLineLength", "Result", 1, 300, empty)
    cv2.createTrackbar("maxLineGap", "Result", 1, 300, empty)


def set_brightness_from_trackbar(cap):
    cap.set(10, cv2.getTrackbarPos("Brightness", "Result"))


def set_treshold_from_trackbar(cap, img):
    ret, thresh1 = cv2.threshold(img, cv2.getTrackbarPos("BinaryThreshold", "Result"), 255, cv2.THRESH_BINARY)
