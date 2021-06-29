#!/bin/python3
import sys
import cv2
import logging
sys.path.append('/home/pi/pren/pren-robo-cube-ipcv/')

from configparser import ConfigParser
from src.common.movement.drive import Drive
from src.common.movement.climb import Climb
from src.common.communication.serial_handler import SerialHandler

from src.a_detect_pictogram import course_detect_pictogram
from src.b_find_stair_center import course_find_stair_center
from src.c_pathfinding import course_pathfinding
from src.common.camera.camera import Camera
from src.common.models.path import Path
from src.d_climb_stair import course_climb_stair
from src.e_find_pictogram import course_find_pictogram

def start():
    conf_parser = ConfigParser()
    conf_parser.read("resources/config.ini")

    serial = SerialHandler()
    drive = Drive(serial)
    climb = Climb(serial)
    camera = Camera()

    climb.head_up_slow(10)  # tilt slightly forward to see pictogram on ground
    pictogram = course_detect_pictogram.run(camera=camera)
    climb.head_down_fast(10)
    
    snapshot = course_find_stair_center.run(conf=conf_parser["B_FIND_STAIR_CENTER"], camera=camera, drive=drive)
    path: Path = course_pathfinding.run(conf=conf_parser["C_PATHFINDING"], snapshot=snapshot)
    course_climb_stair.run(conf=conf_parser["D_CLIMB_STAIR"], path=path, drive=drive, climb=climb)
    success = course_find_pictogram.run(conf=conf_parser["E_FIND_PICTOGRAM"], pictogram=pictogram,
                                        position_robot=path.get_final_position(), drive=drive)
    if success:
        print("YAY!")


if __name__ == '__main__':
    logging.basicConfig(filename='pren_course_complete.log', level=logging.DEBUG)
    start()
