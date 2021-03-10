import cv2
from pathfinder import Pathfinder
from image_manipulator import ImageManipulator

################################################################
CASCADE_PATH = "../cascades/obstacle.xml"
IMG_PATH = "../images/treppe_130_49_cm.jpg"
#################################################################

img_raw = cv2.imread(IMG_PATH)
image_manipulator = ImageManipulator(img_raw)
img = image_manipulator.transform_to_2d()
cascade = cv2.CascadeClassifier(CASCADE_PATH)
finder = Pathfinder(img)
obstacles = finder.find_obstacles(cascade, min_area=400, scale_val=1.2, neighbours=8)
stair_with_objects = finder.create_stair_with_objects(obstacles)
stair_with_areas = finder.create_stair_passable_areas(stair_with_objects)
# matrice = finder.convert_to_matrice(stair_with_areas)
path = finder.calculate_path(stair_with_areas)
print(path.to_string())
