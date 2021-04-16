from src.common.communication.serial_handler import SerialHandler
from src.common.movement.drive import Drive
from src.common.movement.climb import Climb


def drive_floor(drive: Drive):
    drive.forward(50)
    drive.left(50)
    drive.backward(50)
    drive.right(50)


def climb_step(drive: Drive, climb: Climb):
    duration = 3
    forward_head_mm = 63
    forward_body_mm = 80
    forward_tail_mm = 63
    climb.head_up(duration)
    drive.forward(forward_head_mm)
    climb.body_up(duration)
    drive.forward(forward_body_mm)
    climb.body_up(duration)
    drive.forward(forward_tail_mm)


def main():
    handler = SerialHandler()
    drive = Drive(handler)
    climb = Climb(handler)
    drive_floor(drive)
    climb_step(drive, climb)


if __name__ == '__main__':
    main()
