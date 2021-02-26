import cv2
import pyttsx3  # text 2 speech
import cascade_utils as utils

################################################################
CASCADE_PATH = "..\\cascade\\"
paths = ['hammer.xml', 'sandwich.xml', 'rule.xml', 'paint.xml', 'pencil.xml']  # PATH OF THE CASCADE
cameraNo = 0  # CAMERA NUMBER
objectNames = ['hammer', 'sandwich', 'rule', 'paint', 'pencil']  # OBJECT NAMES TO DISPLAY
frameWidth = 640  # DISPLAY WIDTH 640
frameHeight = 480  # DISPLAY HEIGHT 480
color = (255, 0, 255)
objectCount = 3000  # how many objects to find for recognition
#################################################################


def echo_statistics(stats):
    t2s = pyttsx3.init()
    t2s.setProperty('voice', t2s.getProperty('voices'))
    values = stats.values()
    if sum(values) <= 0:
        return
    for k, v in stats.items():
        if v != max(values):
            continue
        t2s.say(k)
        t2s.runAndWait()


def main():
    cap = cv2.VideoCapture(cameraNo)
    cap.set(3, frameWidth)
    cap.set(4, frameHeight)

    utils.create_trackbar(frameWidth, frameHeight)

    cascades = []
    for c in paths:
        cascades.append(cv2.CascadeClassifier(CASCADE_PATH + c))

    while True:
        counter = 0
        stats = {'hammer': 0, 'sandwich': 0, 'rule': 0, 'paint': 0, 'pencil': 0}

        while counter < objectCount:
            utils.set_brightness_from_trackbar(cap=cap)
            success, img = cap.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            utils.set_treshold_from_trackbar(cap=cap, img=gray)

            count, obj = utils.detect_and_display_object(img=img, gray=gray, cascades=cascades, object_names=objectNames,
                                                         color=color)
            counter += count
            if obj is not None:
                stats[obj] += 1

            cv2.imshow("Result", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        echo_statistics(stats)


main()
