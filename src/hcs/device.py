"""

"""

import numpy as np
import serial

from .helper import raise_for_result


class HCS:
    """
    Parent for all HCS devices.
    """
    CR = b"\r"
    ACK = b"OK"

    SET_DECIMALS = {
        "U": None,
        "I": None
    }

    DISPLAY_DECIMALS_I = {
        "U": None,
        "I": None
    }

    def __init__(self, port="/dev/ttyUSB0", max_voltage=None, max_current=None):
        self.port = port
        self.max_voltage = max_voltage
        self.max_current = max_current
        self.serial = serial.Serial(port=self.port, baudrate=9600, timeout=0.5)
        self.__enter__()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.serial.__exit__()

    def _write(self, cmd):
        """

        :param cmd: (bytes) command to send. e.g. b"GETS"
        :return: (bytes) response
        """
        print(cmd)
        self.serial.write(cmd + self.CR)
        return self._read()

    def _read(self):
        """
        :return: result
        """
        result = self.serial.read_until(self.ACK + self.CR)
        # command not accepted
        if result == b"":
            raise Exception("Command failed")
        else:
            return result.rstrip(self.ACK + self.CR)

    @staticmethod
    def _parse_result(result, decimals):
        """
        Parse result bytes into floats for voltage and current
        :param result: (bytes) result read from serial
        :return:
        """
        if decimals["U"] is None or decimals["I"] is None:
            raise NotImplementedError
        voltage = float(result[0:(2 + decimals["U"])]) / 10 ** decimals["U"]
        current = float(result[(2 + decimals["U"]):]) / 10 ** decimals["I"]
        return voltage, current

    def set_output(self, on):
        """
        Set output on/off
        :param on: (bool)
        :return:
        """
        value = b"1" if on else b"0"
        self._write(b"SOUT" + value)
        return True

    def enable(self):
        """
        Enable output
        """
        return self.set_output(True)

    def disable(self):
        """
        Disable output
        """
        return self.set_output(False)

    def get_preset(self):
        """
        Gets the preset voltage/current values
        :return: (tuple) voltage, current
        """
        result = self._write(b"GETS")
        return self._parse_result(result, self.SET_DECIMALS)

    def get_display(self):
        """
        Gets the preset voltage/current values and wether supply is in CC mode (else it is CV)
        :return: (tuple) voltage, current, cc
        """
        result = self._write(b"GETD")
        cc = True if result[-1] == b"1" else False
        return *self._parse_result(result, self.DISPLAY_DECIMALS_I), cc

    def set_voltage(self, voltage):
        """
        Sets the desired voltage, raises if voltage >= soft limit
        :param voltage: (float)
        :return:
        """
        assert self.max_voltage is None or voltage <= self.max_voltage,\
            "Invalid range.\n{} is larger than soft limit of {}".format(voltage, self.max_voltage)
        assert voltage >= 0.8, "Negative or voltage <= 0.8 given"
        voltage_bytes = "{:0{}d}".format(round(voltage * 10**self.SET_DECIMALS["U"]),
                                         self.SET_DECIMALS["U"] + 2).encode()
        self._write(b"VOLT" + voltage_bytes)
        return True

    def set_current(self, current):
        """
        Sets the desired current, raises if current >= soft limit
        :param current: (float)
        :return:
        """
        assert self.max_current is None or current <= self.max_current,\
            "Invalid range.\n{} is larger than soft limit of {}".format(current, self.max_current)
        assert current >= 0.1, "Negative or zero current given"
        current_bytes = "{:0{}d}".format(round(current * 10 ** self.SET_DECIMALS["I"]),
                                         self.SET_DECIMALS["I"] + 2).encode()
        self._write(b"CURR" + current_bytes)
        return True


class HCS3202(HCS):
    SET_DECIMALS = {
        "U": 1,
        "I": 1
    }

    DISPLAY_DECIMALS_I = {
        "U": 2,
        "I": 2
    }
