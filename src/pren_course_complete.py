from src.a_detect_pictogram import course_detect_pictogram
from src.b_find_stair_center import course_find_stair_center
from src.c_pathfinding import course_pathfinding
from src.common.camera.camera import Camera
from src.common.models.path import Path
from src.d_climb_stair import course_climb_stair
from src.e_find_pictogram import course_find_pictogram
from src.common.communication.serial_handler import SerialHandler
from configparser import ConfigParser
import logging


def start():
    serial = SerialHandler()
    logging.basicConfig(level=logging.DEBUG)
    conf_parser = ConfigParser()
    conf_parser.read("resources/config.ini")
    camera = Camera()

    pictogram = course_detect_pictogram.run()
    snapshot = course_find_stair_center.run(conf=conf_parser["B_FIND_STAIR_CENTER"], serial=serial, camera=camera)
    path: Path = course_pathfinding.run(conf=conf_parser["C_PATHFINDING"], snapshot=snapshot)
    course_climb_stair.run(conf=conf_parser["D_CLIMB_STAIR"], path=path, serial=serial)
    success = course_find_pictogram.run(conf=conf_parser["E_FIND_PICTOGRAM"], pictogram=pictogram,
                                        position_robot=path.get_final_position(), serial=serial)
    if success:
        print("YAY!")


if __name__ == '__main__':
    start()
