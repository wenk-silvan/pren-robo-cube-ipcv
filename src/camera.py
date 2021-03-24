import cv2


class Camera:
    def __init__(self, configuration):
        cap = cv2.VideoCapture(int(configuration["camera_number"]))
        cap.set(3, int(configuration["camera_frame_width"]))
        cap.set(4, int(configuration["camera_frame_height"]))

    def snapshot(self):
        pass
