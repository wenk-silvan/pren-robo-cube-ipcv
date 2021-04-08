#!/usr/bin/env python3
import serial
import logging
logging.basicConfig(filename='communication.log', filemode='w', level=logging.DEBUG)


# Returns True if the byteArray is of length 4 and its checksum is valid
def checksum(byte_array):
    if len(byte_array) == 4:
        if (sum(byte_array[0:3]) % 256) == byte_array[3]:
            return True
    return False


class SerialHandler:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        self.ser.flush()
        logging.info("Serial connection established")

    # sends a byteArray of length 4 to the partner (3 data bytes + checksum)
    def send_command(self, byte_array):

        data = byte_array + (sum(byte_array) % 256).to_bytes(1, byteorder='big', signed=True)
        self.ser.write(data)

        answer = self.ser.read(4)
        if checksum(answer):
            if answer[0:3].decode('utf-8').rstrip() == 'ok!':
                logging.debug("Successfully sent Command")
                return True

        return False

    # Check and return status of the Microcontroller
    def check_status(self, byte_array):

        data = byte_array + (sum(byte_array) % 256).to_bytes(1, byteorder='big', signed=True)
        self.ser.write(data)

        answer = self.ser.read(4)
        if checksum(answer):
            return answer

        return False
