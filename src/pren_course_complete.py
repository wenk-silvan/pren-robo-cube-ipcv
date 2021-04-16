from src.a_detect_pictogram import course_detect_pictogram
from src.b_find_stair_center import course_find_stair_center
from src.c_pathfinding import course_pathfinding
from src.common.models.path import Path
from src.d_climb_stair import course_climb_stair
from src.e_find_pictogram import course_find_pictogram


def start():
    pictogram = course_detect_pictogram.run()
    snapshot = course_find_stair_center.run()
    path: Path = course_pathfinding.run(snapshot=snapshot)
    position = course_climb_stair.run(path=path)
    success = course_find_pictogram.run(pictogram=pictogram, position_robot=path.get_final_position())
    if success:
        print("YAY!")


if __name__ == '__main__':
    start()
