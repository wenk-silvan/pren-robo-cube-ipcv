import cv2

from src.c_pathfinding.pathfinder import Pathfinder
from src.common.camera.camera import Camera
from src.common.image_manipulator import ImageManipulator
from configparser import ConfigParser


def get_configuration(path):
    config_object = ConfigParser()
    config_object.read(path)
    return config_object["C_PATHFINDING"]


def main():
    conf = get_configuration("../../resources/config.ini")
    # img_raw = Camera().snapshot()
    img_raw = cv2.imread(conf["img_3_path"])
    image_manipulator = ImageManipulator(img_raw)
    img = image_manipulator.transform_to_2d()
    finder = Pathfinder(img, conf)
    obstacles = finder.find_obstacles(cv2.CascadeClassifier(conf["cascade_path"]))
    stair_with_objects = finder.create_stair_with_objects(obstacles)
    stair_with_areas = finder.create_stair_passable_areas(stair_with_objects)
    path = finder.calculate_path(stair_with_areas)
    print(path.to_string())


main()
