import cv2
import numpy as np


def _draw(p1, p2, img):
    if img is None: return
    cv2.line(img, p1, p2, (255, 0, 0), 2)


def _draw_lines(lines, img, width):
    if lines is None:
        return
    y_values = []
    drawn = []

    for x in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[x]:
            if abs(y1 - y2) > 10:
                continue

            if len(y_values) == 0:
                p1 = (20, y1)
                p2 = (width - 20, y2)
                _draw(p1=p1, p2=p2, img=img)
                y_values.append(y1)
                drawn.append((p1, p2))

            has_neighbour = False
            for y in y_values:
                if len(y_values) > 0 and abs(y - y1) < 30:
                    has_neighbour = True
                    break

            if not has_neighbour:
                p1 = (20, y1)
                p2 = (width - 20, y2)
                _draw(p1=p1, p2=p2, img=img)
                y_values.append(y1)
                drawn.append((p1, p2))
    return drawn


def empty():
    pass

cv2.namedWindow("Result")
cv2.createTrackbar("Rho", "Result", 1, 10, empty)
cv2.createTrackbar("Theta", "Result", 1, 10, empty)
cv2.createTrackbar("Threshold", "Result", 1, 300, empty)
cv2.createTrackbar("minLineLength", "Result", 1, 300, empty)
cv2.createTrackbar("maxLineGap", "Result", 1, 300, empty)

while True:
    img = cv2.imread("../../images/treppe_mit_hindernisse_1.jpg")
    gauss = cv2.GaussianBlur(img, (5, 5), 0, 0)
    gray = cv2.cvtColor(gauss, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, 80, 240, 3)
    lines = cv2.HoughLinesP(
        canny,
        rho=cv2.getTrackbarPos("Rho", "Result"),
        theta=cv2.getTrackbarPos("Theta", "Result") * np.pi / 180,
        threshold=cv2.getTrackbarPos("Threshold", "Result"),
        minLineLength=cv2.getTrackbarPos("minLineLength", "Result"),
        maxLineGap=cv2.getTrackbarPos("maxLineGap", "Result")
    )

    drawnLines = _draw_lines(lines, img, img.shape[1])
    cv2.imshow("Result", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break