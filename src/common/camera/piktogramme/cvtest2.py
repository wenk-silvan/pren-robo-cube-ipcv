import time
import picamera
import picamera.array
import cv2

with picamera.PiCamera() as camera:

    with picamera.array.PiRGBArray(camera) as stream:
        camera.capture(stream, format='bgr')
        # At this point the image is available as stream.array
        image = stream.array

