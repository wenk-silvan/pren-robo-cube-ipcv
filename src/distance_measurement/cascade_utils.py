import os
import cv2

# tutorial: https://www.youtube.com/watch?v=XrCAvs9AePM&ab_channel=LearnCodeByGaming

def generate_negative_description_file():
    with open('images_labeled/negative/hammer.txt', 'w') as f:
        for filename in os.listdir('./images/negative/hammer_small'):
            f.write('images/negative/hammer_small/' + filename + '\n')

def detect_and_display_object(img, gray, cascades, objectNames, color):
    l = list(range(1, len(objectNames) + 1))
    zipbObj = zip(objectNames, l)
    objectDict = dict(zipbObj)
    counter = 0
    o = None

    scaleVal = 1.05 + (cv2.getTrackbarPos("Scale", "Result") / 1000)
    neighbours = cv2.getTrackbarPos("Neighbours", "Result")
    for c in cascades:
        objects = c.detectMultiScale(gray, scaleVal, neighbours)
        for (x, y, w, h) in objects:
            area = w * h
            minArea = cv2.getTrackbarPos("Min Area", "Result")
            if area > minArea:
                o = objectNames[cascades.index(c)]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 3)
                cv2.putText(img, o, (x, y - 5), cv2.CASCADE_FIND_BIGGEST_OBJECT, 1, color, 2)
                roi_color = img[y:y + h, x:x + w]
                counter += 1

    return counter, o

def empty(a):
    pass

def create_trackbar(width, height):
    cv2.namedWindow("Result")
    cv2.resizeWindow("Result", width, height)
    # cv2.createTrackbar("Scale", "Result", 200, 1000, empty)
    cv2.createTrackbar("Neighbours", "Result", 6, 50, empty)
    # cv2.createTrackbar("Min Area", "Result", 400, 100000, empty)
    # cv2.createTrackbar("Brightness", "Result", 100, 255, empty)
    cv2.createTrackbar("BinaryThreshold", "Result", 123, 255, empty)

def add_trackbar_hough():
    cv2.createTrackbar("Rho", "Result", 1, 10, empty)
    cv2.createTrackbar("Theta", "Result", 1, 10, empty)
    cv2.createTrackbar("Threshold", "Result", 1, 300, empty)
    cv2.createTrackbar("minLineLength", "Result", 1, 300, empty)
    cv2.createTrackbar("maxLineGap", "Result", 1, 300, empty)

def set_brightness_from_trackbar(cap):
    cameraBrightness = cv2.getTrackbarPos("Brightness", "Result")
    cap.set(10, cameraBrightness)
    
def set_treshold_from_trackbar(cap, img):
    binaryThreshold = cv2.getTrackbarPos("BinaryThreshold", "Result")
    ret, thresh1 = cv2.threshold(img, binaryThreshold, 255, cv2.THRESH_BINARY)
