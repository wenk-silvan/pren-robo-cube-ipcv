import logging


class Sensor:
    def __init__(self, serial_handler):
        self._serial_handler = serial_handler

    def left(self):
        sensor_id = 0
        return self._read_sensor(sensor_id)

    def front_left(self):
        sensor_id = 1
        return self._read_sensor(sensor_id)

    def front_right(self):
        sensor_id = 2
        return self._read_sensor(sensor_id)

    def right(self):
        sensor_id = 3
        return self._read_sensor(sensor_id)

    def down_front(self):
        sensor_id = 4
        return self._read_sensor(sensor_id)

    def down_center(self):
        sensor_id = 5
        return self._read_sensor(sensor_id)

    def down_tail(self):
        sensor_id = 6
        return self._read_sensor(sensor_id)

    def _read_sensor(self, sensor_id):
        """
        Reads the value from a given sensor.
        :param sensor_id:
        :return: the distance in mm to the next object (dist > 100mm are not accurate)
        """
        if sensor_id < 0 or sensor_id > 6:
            logging.warning("There is no Sensor with id[%s]", str(sensor_id))
            raise ValueError

        command = b'\x40' + sensor_id.to_bytes(1, byteorder='big', signed=False) + b'\x00'
        answer = self._serial_handler.send_command(command)

        return answer[2]
