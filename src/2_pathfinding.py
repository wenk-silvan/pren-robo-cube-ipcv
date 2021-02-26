import cv2
from pathfinder import Pathfinder

################################################################
CASCADE_PATH = "..\\cascade\\obstacle.xml"
IMG_PATH = "../images/treppe_mit_hindernisse_1_centered.jpg"
#################################################################

img = cv2.imread(IMG_PATH)
cascade = cv2.CascadeClassifier(CASCADE_PATH)
finder = Pathfinder(img)
obstacles = finder.find_obstacles(cascade, min_area=400, scale_val=1.2, neighbours=8)
stair_with_objects = finder.create_stair_with_objects(obstacles)
stair_with_areas = finder.create_stair_passable_areas(stair_with_objects)
# matrice = finder.convert_to_matrice(stair_with_areas)
path = finder.calculate_path(stair_with_areas)
print(path.to_string())
