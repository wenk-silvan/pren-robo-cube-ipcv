import cv2
from src.stair.pathfinding.pathfinder import Pathfinder
from src.camera.image_manipulator import ImageManipulator
from configparser import ConfigParser


def get_configuration(path):
    config_object = ConfigParser()
    config_object.read(path)
    return config_object["CONFIGURATION"]


def main():
    conf = get_configuration("../config.ini")
    img_raw = cv2.imread(conf["img_path"])
    image_manipulator = ImageManipulator(img_raw)
    img = image_manipulator.transform_to_2d()
    finder = Pathfinder(img, conf)
    obstacles = finder.find_obstacles(cv2.CascadeClassifier(conf["cascade_path"]))
    stair_with_objects = finder.create_stair_with_objects(obstacles)
    stair_with_areas = finder.create_stair_passable_areas(stair_with_objects)
    # matrice = finder.convert_to_matrice(stair_with_areas)
    path = finder.calculate_path(stair_with_areas)
    print(path.to_string())


main()
