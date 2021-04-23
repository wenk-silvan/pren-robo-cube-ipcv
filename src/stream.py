# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import logging
import cv2
import numpy as np
import socketserver
from threading import Condition
from http import server
from src.common.object_detection import ObjectDetection
import picamera
from configparser import ConfigParser
from src.b_find_stair_center.image_processing import ImageProcessing
from src.b_find_stair_center.stair_detection import StairDetection

PAGE = """\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    def draw_lines(self, lines, img, color):
        if lines is None:
            return
        for l in lines:
            p1 = (l.p1.x, l.p1.y)
            p2 = (l.p2.x, l.p2.y)
            if not p1 or not p2:
                continue
            cv2.line(img, p1, p2, color, 2)

    def detect_obstacles(self, img):
        detection_obstacle_scale = 2.5
        detection_obstacle_neighbours = 3
        obstacle_detection = ObjectDetection("resources/cascades/obstacle/", ["obstacle.xml"])
        obstacles = obstacle_detection.detect(img, 2000, 30000, detection_obstacle_scale, detection_obstacle_neighbours)
        violet = (143, 0, 255)
        obstacle_detection.draw(img, obstacles, violet)

    def detect_pictograms(self, img):
        detection_pictogram_scale = 1.2
        detection_pictogram_neighbours = 3
        pictogram_detection = ObjectDetection("resources/cascades/pictogram/",
                                              ['hammer.xml', 'sandwich.xml', 'rule.xml', 'paint.xml', 'pencil.xml'])
        pictograms = pictogram_detection.detect(img, 1000, 15000, detection_pictogram_scale,
                                                detection_pictogram_neighbours)
        yellow = (255, 255, 0)
        pictogram_detection.draw(img, pictograms, yellow)

    def detect_stair(self, conf, img):
        stair = StairDetection(conf, ImageProcessing(conf))
        lines_vertical, lines_horizontal = stair.detect_lines(img)
        self.draw_lines(lines_horizontal, img, (255, 0, 0))
        self.draw_lines(lines_vertical, img, (0, 255, 0))

    def process_image(self, frame):
        config_object = ConfigParser()
        config_object.read("resources/config.ini")
        conf = config_object["B_FIND_STAIR_CENTER"]

        cv2.CV_LOAD_IMAGE_COLOR = 1
        npframe = np.fromstring(frame, dtype=np.uint8)
        image = cv2.imdecode(npframe, cv2.CV_LOAD_IMAGE_COLOR)
        self.detect_pictograms(image)
        self.detect_obstacles(image)
        self.detect_stair(conf, image)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, jpg = cv2.imencode('.jpg', image, encode_param)
        return jpg

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    img = self.process_image(frame)
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(img)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    # Uncomment the next line to change your Pi's Camera rotation (in degrees)
    # camera.rotation = 90
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
