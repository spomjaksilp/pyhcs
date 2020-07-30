"""

"""
import logging

import numpy as np
import serial


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

    DISPLAY_DECIMALS = {
        "U": None,
        "I": None
    }

    DEVICE_LIMITS = {
        "U": None,
        "I": None,
    }

    def __init__(self, port="/dev/ttyUSB0", limit_voltage=None, limit_current=None, blind=False):
        """
        :param port: (str) serial port
        :param limit_voltage: (float) voltage soft-limit
        :param limit_current: (float) current soft-limit
        :param blind: (bool) switch to skip device detection
        """
        logging.info("Connecting to serial device at {}".format(port))
        self.port = port
        self.limit_voltage = limit_voltage
        self.limit_current = limit_current
        self.serial = serial.Serial(port=self.port, baudrate=9600, timeout=0.5)
        self.max_voltage, self.max_current = self.get_max() if not blind else (1e3, 1e3)
        logging.info("Max ratings for {}: {}V and {}A".format(self.port, self.max_voltage, self.max_current))
        if self.limit_voltage is None:
            self.limit_voltage = self.max_voltage
        if self.limit_current is None:
            self.limit_current = self.max_current
        logging.info("Configuration soft-limits to {}V and {}A".format(limit_voltage, limit_current))
        assert self.limit_voltage <= self.max_voltage, "Voltage limit > device maximum"
        assert self.limit_current <= self.max_voltage, "Current limit > device maximum"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.info("Terminating serial connection to {}".format(self.port))
        self.serial.__exit__()

    @property
    def min_voltage(self):
        """
        Returns the minimal voltage for this device
        :return: (float) minimal voltage
        """
        if self.DEVICE_LIMITS["U"] is None:
            raise NotImplementedError
        else:
            return self.DEVICE_LIMITS["U"][0]

    @property
    def min_current(self):
        """
        Returns the minimal current for this device
        :return: (float) minimal voltage
        """
        if self.DEVICE_LIMITS["I"] is None:
            raise NotImplementedError
        else:
            return self.DEVICE_LIMITS["I"]

    def _write(self, cmd):
        """

        :param cmd: (bytes) command to send. e.g. b"GETS"
        :return: (bytes) response
        """
        logging.debug("Writing {}".format(cmd + self.CR))
        self.serial.write(cmd + self.CR)

    def _read(self):
        """
        :return: (bytes) result
        """
        result = self.serial.read_until(self.ACK + self.CR)
        logging.debug("Received answer {}".format(result))
        # command not accepted
        if result == b"":
            return False, b""
        else:
            return True, result.rstrip(self.ACK + self.CR)

    def _execute(self, cmd):
        """
        Executes a given command and evaluates the result
        :param cmd: (bytes) command to send. e.g. b"GETS"
        :return: (bytes) result
        """
        self._write(cmd)
        success, answer = self._read()
        if success:
            return answer
        else:
            raise Exception("Command {} did not receive ACK".format(cmd.decode()))

    def get_max(self):
        """
        Queries max voltage and current
        :return: (tuple) max_voltage, max_voltage
        """
        result = self._execute(b"GMAX")
        return self._parse_result(result, self.SET_DECIMALS)

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
        current = float(result[(2 + decimals["I"]):]) / 10 ** decimals["I"]
        return voltage, current

    def set_output(self, on):
        """
        Set output on/off
        :param on: (bool)
        :return:
        """
        pvalue = b"0" if on else b"1"
        self._execute(b"SOUT" + value)
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
        result = self._execute(b"GETS")
        return self._parse_result(result, self.SET_DECIMALS)

    def get_display(self):
        """
        Gets the preset voltage/current values and wether supply is in CC mode (else it is CV)
        :return: (tuple) voltage, current, cc
        """
        result = self._execute(b"GETD")
        cc = True if result[-1] == b"1" else False
        return *self._parse_result(result[::-1], self.DISPLAY_DECIMALS), cc

    def set_voltage(self, voltage):
        """
        Sets the desired voltage, raises if voltage >= soft limit
        :param voltage: (float)
        :return:
        """
        assert voltage <= self.limit_voltage,\
            "Invalid range! {}V > limit of {}V".format(voltage, self.limit_voltage)
        assert voltage > 0, "Negative voltage given"
        if voltage < self.min_voltage:
            logging.warning("Given voltage {}V < {}V minimum, setting to minimum voltage".format(voltage,
                                                                                                 self.min_voltage))
            voltage = self.min_voltage
        voltage_bytes = "{:0{}d}".format(round(voltage * 10**self.SET_DECIMALS["U"]),
                                         self.SET_DECIMALS["U"] + 2).encode()
        self._execute(b"VOLT" + voltage_bytes)
        return True

    def set_current(self, current):
        """
        Sets the desired current, raises if current >= soft limit
        :param current: (float)
        :return:
        """
        assert current <= self.limit_current,\
            "Invalid range! {}A > limit of {}A".format(current, self.limit_current)
        assert current > 0, "Negative current given"
        if current < self.min_current:
            logging.warning("Given current {}A < {}A minimum, setting to minimum current".format(current,
                                                                                                 self.min_current))
            current = self.min_current
        current_bytes = "{:0{}d}".format(round(current * 10 ** self.SET_DECIMALS["I"]),
                                         self.SET_DECIMALS["I"] + 2).encode()
        self._execute(b"CURR" + current_bytes)
        return True


class HCS3202(HCS):
    SET_DECIMALS = {
        "U": 1,
        "I": 1
    }

    DISPLAY_DECIMALS = {
        "U": 2,
        "I": 2
    }

    DEVICE_LIMITS = {
        "U": 0.8,
        "I": 0.1,
    }
