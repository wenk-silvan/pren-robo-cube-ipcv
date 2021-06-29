import logging
import pyttsx3

from src.a_detect_pictogram import course_detect_pictogram
from src.common.communication.serial_handler import *
from src.common.movement.drive import *
from src.common.movement.direction import *
from src.common.movement.climb import *

ts = pyttsx3.init()
ts.say("Welcome to our Demonstration. I will show you some moves")
ts.runAndWait()

sh = SerialHandler()
climb = Climb(sh)
drive = Drive(sh)

drive.forward(20)
drive.rotate_body_left(20)
drive.backward(20)
drive.rotate_body_right(20)

ts.say("please show me a pictogram")
ts.runAndWait()

course_detect_pictogram.run()