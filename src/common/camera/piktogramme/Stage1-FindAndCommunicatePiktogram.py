import cv2
import pyttsx3  # text 2 speech
from picamera import PiCamera
from picamera.array import PiRGBArray
import time
import pathlib

from imutils.video.pivideostream import PiVideoStream
import imutils

################################################################
wdir = pathlib.Path().absolute()
paths = ['hammer.xml', 'sandwich.xml', 'rule.xml', 'paint.xml', 'pencil.xml']  # PATH OF THE CASCADE
cameraNo = 0  # CAMERA NUMBER
objectNames = ['hammer', 'sandwich', 'rule', 'paint', 'pencil']  # OBJECT NAMES TO DISPLAY
#frameWidth = 640  # DISPLAY WIDTH 640
#frameHeight = 480  # DISPLAY HEIGHT 480
color = (255, 0, 255)
objectCount = 300      # how many objects to find for recognition
#################################################################


# initialize the camera and grab a reference to the raw camera capture
#camera = PiCamera()
#camera.resolution = (frameWidth, frameHeight)
#rawCapture = PiRGBArray(camera)

#camera = PiCamera()
#camera.resolution = (frameWidth, frameHeight)
#rawCapture = PiRGBArray(camera, size=(frameWidth, frameHeight))
vs = PiVideoStream().start()

# allow the camera to warmup
time.sleep(2)

# grab an image from the camera
#rawCapture = PiRGBArray(camera, size=(640, 480))
#camera.capture(rawCapture, format="bgr")
#cap = rawCapture.array


#camera.resolution= (320,240)
#cap = PiRGBArray(camera, size=(320,240))


#cap = cv2.VideoCapture(PiCamera())
#camera.capture(cap, 'jpeg')

#cap.set(3, frameWidth)
#cap.set(4, frameHeight)

t2s = pyttsx3.init()
t2s.setProperty('voice', t2s.getProperty('voices'))


def empty(a):
    pass


# CREATE TRACKBAR
cv2.namedWindow("Result")
#cv2.resizeWindow("Result", frameWidth, frameHeight + 100)
cv2.createTrackbar("Scale", "Result", 200, 1000, empty)
cv2.createTrackbar("Neighbours", "Result", 6, 50, empty)
cv2.createTrackbar("Min Area", "Result", 400, 100000, empty)

# LOAD THE CLASSIFIERS DOWNLOADED
cascades = []
for c in paths:
    cascades.append(cv2.CascadeClassifier(str(wdir) + "/cascades/" + c))


while True:

    counter = 0
    stats = {'hammer': 0, 'sandwich': 0, 'rule': 0, 'paint': 0, 'pencil': 0}

    while counter < objectCount:
        # SET CAMERA BRIGHTNESS FROM TRACKBAR VALUE
        cameraBrightness = cv2.getTrackbarPos("Brightness", "Result")

        frame = vs.read()
        img = imutils.resize(frame)
        
        
        #camera.capture(rawCapture, format='bgr')
        #img = rawCapture.array
        
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # DETECT THE OBJECT USING THE CASCADE
        scaleVal = 1.05 + (cv2.getTrackbarPos("Scale", "Result") / 1000)
        neighbours = cv2.getTrackbarPos("Neighbours", "Result")

        for c in cascades:
            objects = c.detectMultiScale(gray, scaleVal, neighbours)
            # DISPLAY THE DETECTED OBJECTS

            for (x, y, w, h) in objects:
                area = w * h
                minArea = cv2.getTrackbarPos("Min Area", "Result")
                if area > minArea:
                    o = objectNames[cascades.index(c)]
                    cv2.rectangle(img, (x, y), (x + w, y + h), color, 3)
                    cv2.putText(img, o, (x, y - 5), cv2.CASCADE_FIND_BIGGEST_OBJECT, 1, color, 2)
                    roi_color = img[y:y + h, x:x + w]

                    counter += 1
                    stats[o] += 1

            cv2.imshow("Result", img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
                   

    break
cv2.destroyAllWindows()
vs.stop()
print(stats)
# get key with max value
if sum(stats.values()) > 0:
    for k, v in stats.items():
        if v == max(stats.values()):
            t2s.say(k)
            t2s.runAndWait()
