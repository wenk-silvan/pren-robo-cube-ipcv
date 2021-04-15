import cv2

from src.c_pathfinding.pathfinder import Pathfinder
from src.common.image_manipulator import ImageManipulator
from configparser import ConfigParser

from src.common.models.obstacle import Obstacle
from src.common.object_detection import ObjectDetection


def get_configuration(path):
    config_object = ConfigParser()
    config_object.read(path)
    return config_object["C_PATHFINDING"]


def main():
    conf = get_configuration("../../resources/config.ini")
    # img_raw = Camera().snapshot()
    image_raw = cv2.imread(conf["img_3_path"])
    image_manipulator = ImageManipulator(image_raw)
    image = image_manipulator.transform_to_2d((600, 600))
    finder = Pathfinder(image, conf)

    detector = ObjectDetection("../../resources/cascades/obstacle/", ["obstacle.xml"])
    # TODO: Adjust detection parameters
    obstacles = detector.detect(image, 5000, 100000, float(conf["detection_obstacle_scale"]),
                                int(conf["detection_obstacle_neighbours"]))

    detector.draw(image, obstacles, (0, 255, 0))

    stair_with_objects = finder.create_stair_with_objects([Obstacle(o[0], o[1]) for o in obstacles])

    cv2.imshow("Result", image)
    cv2.waitKey(0)

    stair_with_areas = finder.create_stair_passable_areas(stair_with_objects)
    path = finder.calculate_path(stair_with_areas)
    print(path.to_string())


main()
