import cv2
import numpy as np

from src.common.models.point import Point


class ObstacleDetectionYolo:
    def __init__(self, conf):
        yolo_config = conf["detection_yolo_config"]
        yolo_weights = conf["detection_yolo_weights"]
        self.classes = ["brick"]
        self.net = cv2.dnn.readNetFromDarknet(yolo_config, yolo_weights)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

    def detect(self, image):
        height, width, _ = image.shape
        blob = cv2.dnn.blobFromImage(image, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
        self.net.setInput(blob)
        output_layers_name = self.net.getUnconnectedOutLayersNames()
        layer_outputs = self.net.forward(output_layers_name)
        obstacles = []

        for output in layer_outputs:
            for detection in output:
                score = detection[5:]
                class_id = np.argmax(score)
                confidence = score[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    obstacles.append((Point(x, y), Point(x + w, y + h)))
        return obstacles

    def draw(self, img, objects, color):
        [cv2.rectangle(img, (p1.x, p1.y), (p2.x, p2.y), color, 2) for (p1, p2) in objects]
