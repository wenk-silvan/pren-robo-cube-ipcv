#!/usr/bin/env python3
import serial
import logging
logging.basicConfig(filename='communication.log', filemode='w', level=logging.DEBUG)


def checksum(byte_array):
    """
    Checks whether a byte array has a valid checksum or not.
    :param byte_array: of length 4 e.g. b'\x19\x10\x00\x29'
    :return: True for valid checksum, False or failed communication
    """
    if len(byte_array) == 4:
        if (sum(byte_array[0:3]) % 256) == byte_array[3]:
            return True
    return False


class SerialHandler:
    """
    Creates a serial Connection and handles all communication to th STM32 Controller over UART.
    """
    def __init__(self, tty_device='/dev/ttyS0', baud_rate=115200):
        """
        Initializes the Serial connection to the Controller. Depending on the type of Connection (Direct wires or
        though USB, the tty_device might change. tty Devices might be found via "ls /dev/tty*"
        :param tty_device: Device name of the used Connection
        :param baud_rate: Communication speed set on both devices
        """
        self.ser = serial.Serial(tty_device, baud_rate, timeout=1)
        self.ser.flush()
        logging.info("Serial connection established to {} with baud-rate {}".format(tty_device, baud_rate))

    def send_command(self, byte_array):
        """
        Sends a byte array of 3 bytes + 1 byte checksum to the STM32 Controller and receives a status message.
        :param byte_array: of length 3 e.g. b'\x19\x10\x00'
        """
        data = byte_array + (sum(byte_array) % 256).to_bytes(1, byteorder='big', signed=False)

        logging.debug("sending command: " + str(data))
        self.ser.write(data)

        answer = self.ser.read(4)
        logging.debug("received answer " + str(answer))

        if checksum(answer):
            if answer[0:3].decode('utf-8').rstrip() == 'ok!':
                logging.debug("successfully sent Command")
                return True
        # TODO Implement handling if "nok" received! try 3 times?

        return False

    def check_status(self, byte_array):
        """
        Asks the STM32 Controller to provide information over different registers.
        Status of motors, position of servos, readings of sensors
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
