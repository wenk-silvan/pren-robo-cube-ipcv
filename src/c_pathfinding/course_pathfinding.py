from configparser import ConfigParser
from src.c_pathfinding.pathfinder import Pathfinder
from src.common.image_manipulator import ImageManipulator
from src.common.models.obstacle import Obstacle
from src.common.object_detection import ObjectDetection


def run(conf, snapshot):
    image_manipulator = ImageManipulator(snapshot)
    image = image_manipulator.transform_to_2d((600, 600))
    finder = Pathfinder(image, conf)

    # TODO: Adjust detection parameters
    detector = ObjectDetection("resources/cascades/obstacle/", ["obstacle.xml"])
    obstacles = detector.detect(image, 5000, 100000, float(conf["detection_obstacle_scale"]),
                                int(conf["detection_obstacle_neighbours"]))
    detector.draw(image, obstacles, (0, 255, 0))
    stair_with_objects = finder.create_stair_with_objects([Obstacle(o[0], o[1]) for o in obstacles])
    stair_with_areas = finder.create_stair_passable_areas(stair_with_objects)
    paths = finder.calculate_path(stair_with_areas)
    path = Pathfinder.determine_best_path(paths)
    print("====== All paths: ======")
    for p in paths:
        print(p.to_string())

    print("====== Fastest path: ======")
    print(path.to_string())
    return path


if __name__ == '__main__':
    conf_parser = ConfigParser()
    conf_parser.read("resources/config.ini")
    conf = conf_parser["B_FIND_STAIR_CENTER"]
    image_raw = cv2.imread(conf["img_3_path"])
    run(conf=conf, snapshot=image_raw)
