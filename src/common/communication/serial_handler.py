#!/usr/bin/env python3
import time
import serial
import logging
logging.basicConfig(filename='communication.log', filemode='w', level=logging.DEBUG)


def checksum(byte_array):
    """
    Checks whether a byte array has a valid checksum or not.
    :param byte_array: of length 4 e.g. b'\x19\x10\x00\x29'
    :return: True for valid checksum, False or failed communication
    """
    if (sum(byte_array[0:3]) % 256) == byte_array[3]:
        return True
    return False


class SerialHandler:
    """
    Creates a serial Connection and handles all communication to th STM32 Controller over UART.
    """
    def __init__(self, serial_object=None):
        """=serial.Serial('/dev/ttyS0', 115200, timeout=1)
        Initializes the Serial connection to the Controller. Depending on the type of Connection (Direct wires or
        though USB, the tty_device might change. tty Devices might be found via "ls /dev/tty*"
        :param serial_object: Optional pre initialized serial object
        """
        if serial_object is None:
            serial_object = serial.Serial('/dev/ttyS0', 115200, timeout=1)

        self.ser = serial_object
        self.ser.flush()
        logging.info("Serial connection established to {} with baud-rate {}".format(self.ser.name, self.ser.baudrate))

    def send_command(self, byte_array):
        """
        Sends a byte array of 3 bytes + 1 byte checksum to the STM32 Controller and receives a status message.
        :param byte_array: of length 3 e.g. b'\x19\x10\x00'
        """
        data = byte_array + (sum(byte_array) % 256).to_bytes(1, byteorder='big', signed=False)
        logging.debug("sending command: " + str(data))

        answer = None
        answer_valid = False

        # Try 5 times to get a valid answer (checksum and not "nok") before sending False back to the caller
        for i in range(5):
            self.ser.write(data)
            answer = self.ser.read(4)
            if checksum(answer):
                if answer[0:3].decode('utf-8').rstrip() != 'nok':
                    logging.debug("received valid answer " + str(answer))
                    answer_valid = True
                    break
            time.sleep(0.05)

        if answer_valid:
            return answer

        logging.warning("no valid answer received!")
        return False

    def check_status(self, byte_array):
        """
        Asks the STM32 Controller to provide information over different registers.
        Status of motors, readings of sensors, status overall
        :param byte_array: Defines what registers to read from
        :return: 4 bytes from STM32 Controller or False if checksum was wrong
        """
        data = byte_array + (sum(byte_array) % 256).to_bytes(1, byteorder='big', signed=False)
        logging.debug("check status: " + data)
        self.ser.write(data)

        answer = self.ser.read(4)
        logging.debug("received answer " + str(answer))
        if checksum(answer):
            return answer

        return False
