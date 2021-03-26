from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import time
import cascade_utils as utils

################################################################
CASCADE_PATH = "cascade\\obstacle.xml"
CAMERA_NO = 0  # CAMERA NUMBER
FRAME_WIDTH = 1280  # DISPLAY WIDTH 640
FRAME_HEIGHT = 960  # DISPLAY HEIGHT 480
color = (255, 0, 255)
FONT_COLOR = (255, 0, 0)
PIVOT_WIDTH_MM = 160
OBJECT_TEXT = "Ziegel"
#################################################################

def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

def drawMeasurment(img, distanceInPixel, pixelPerMillimeter, offset):
    cv2.putText(img, "{:.1f}mm".format(distanceInPixel * pixelPerMillimeter),
        offset, cv2.FONT_HERSHEY_SIMPLEX,
        0.65, FONT_COLOR, 2)

def drawMidpointLines(img, tltrX, tltrY, blbrX, blbrY, tlblX, tlblY, trbrX, trbrY):
    cv2.line(img, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
        (255, 0, 255), 2)
    cv2.line(img, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
        (255, 0, 255), 2)

def drawMidpoints(img, tltrX, tltrY, blbrX, blbrY, tlblX, tlblY, trbrX, trbrY):
    cv2.circle(img, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
    cv2.circle(img, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
    cv2.circle(img, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
    cv2.circle(img, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

def findLeftPointOfNearestObstacle(rightObjectA, leftRightTuples):
    nearest = leftRightTuples[0][0]
    distance = nearest[0] - rightObjectA[0]

    for (left, right) in leftRightTuples:
        oldDistance = nearest[0] - rightObjectA[0]
        newDistance = left[0] - rightObjectA[0]
        if (newDistance > 0 and newDistance < oldDistance):
            nearest = left
            distance = newDistance
    return nearest, distance
    
def measureDistance(img, pivot, objects):
    if(len(objects) == 0 or pivot == None): return
    edged = cv2.Canny(img, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)
    (px, py, pw, ph) = pivot
    
    # The pixel per metric ratio with a known with in millimeters of the pivot
    pixelsPerMetric = PIVOT_WIDTH_MM / pw
    leftRightTuples = []
    
    for o in objects:
        (x, y, w, h) = o
        tl = (x, y)
        tr = (x + w, y)
        bl = (x, y + h)
        br = (x + w, y + h)
        top = (tltrX, tltrY) = midpoint(tl, tr)
        bottom = (blbrX, blbrY) = midpoint(bl, br)
        left = (tlblX, tlblY) = midpoint(tl, bl)
        right = (trbrX, trbrY) = midpoint(tr, br)        
        leftRightTuples.append((left, right))
        drawMidpoints(img, tltrX, tltrY, blbrX, blbrY, tlblX, tlblY, trbrX, trbrY)

        # if (o != pivot):
        #     drawMidpointLines(img, tltrX, tltrY, blbrX, blbrY, tlblX, tlblY, trbrX, trbrY)        
        #     drawMeasurment(img, dist.euclidean(top, bottom), pixelsPerMetric, (int(tltrX - 15), int(tltrY - 10)))
        #     drawMeasurment(img, dist.euclidean(left, right), pixelsPerMetric, (int(trbrX + 10), int(trbrY)))
    
    distances = []
    # sort x-coordinates of objects from left to right
    leftRightTuples.sort(key=lambda tup: tup[0][0])
    copy = leftRightTuples.copy()

    # measure and draw distances of obstacles which don't overlap horizontally, 
    for i in range(0, len(leftRightTuples) - 1):
        copy.pop(0)
        rightObjectA = leftRightTuples[i][1]
        leftObjectB, horizontal_distance = findLeftPointOfNearestObstacle(rightObjectA, copy)
        vertical_distance = abs(rightObjectA[1] - leftObjectB[1])
        if (horizontal_distance > 0 and vertical_distance < 20):
            drawMeasurment(img, horizontal_distance, pixelsPerMetric, (int(rightObjectA[0] + 10), int(rightObjectA[1])))
    return img

def main():
    cap = cv2.VideoCapture("videos\\01_hand_done.mp4")

    if (cap.isOpened()== False):
        print("Error opening video stream or file")

    cap.set(3, FRAME_WIDTH)
    cap.set(4, FRAME_HEIGHT)

    while True:
        #utils.set_brightness_from_trackbar(cap = cap)
        #success, img = cap.read()
        img = cv2.imread("images/treppe_mit_hindernisse_1.jpg")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #utils.set_treshold_from_trackbar(cap = cap, img = gray)
        scaleVal = 1.2
        neighbours = 8
        minArea = 400
        
        # OBJEKT ERKENNEN
        cascade = cv2.CascadeClassifier(CASCADE_PATH)
        obstacles = []
        pivot = (0, 0, 0, 0)
        for (x, y, w, h) in cascade.detectMultiScale(gray, scaleVal, neighbours):
            if w * h < minArea: continue
            obstacles.append((x, y, w, h))
            # Get object with greatest width
            if (w > pivot[2]):
                pivot = (x, y, w, h)
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 3)
            cv2.putText(img, OBJECT_TEXT, (x, y - 5), cv2.CASCADE_FIND_BIGGEST_OBJECT, 1, color, 2)
            roi_color = img[y:y + h, x:x + w]
        cv2.imshow("Result", img)

        if (pivot[2] > 0 and len(obstacles) > 1):
            markedImg = measureDistance(img = img, pivot = pivot, objects = obstacles)
            cv2.imshow("Result", markedImg)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
main()

