import pytest
import numpy as np

from hcs import HCS3202

PORT = "/dev/ttyUSB0"
VOLTAGES = np.linspace(1, 10, 2)
CURRENTS = np.linspace(0.1, 2, 2)


class TestSetter:
    @pytest.mark.parametrize("voltage", VOLTAGES)
    def test_set_voltage(self, voltage):
        # assemble
        with HCS3202(PORT) as device:
            # act
            result = device.set_voltage(voltage)
        # assert
        assert result

    def test_set_negative(self):
        # assemble
        with HCS3202(PORT) as device:
            # act & assert
            with pytest.raises(AssertionError, match=r"^Negative.*"):
                result = device.set_voltage(-1)

    def test_set_over(self):
        # assemble
        with HCS3202(PORT, max_voltage=1) as device:
            # act & assert
            with pytest.raises(AssertionError, match=r"^Invalid.*"):
                result = device.set_voltage(90)

    @pytest.mark.parametrize("current", CURRENTS)
    def test_set_current(self, current):
        # assemble
        with HCS3202(PORT) as device:
            # act
            result = device.set_current(current)
        # assert
        assert result

    def test_set_negative(self):
        # assemble
        with HCS3202(PORT) as device:
            # act & assert
            with pytest.raises(AssertionError, match=r"^Negative.*"):
                result = device.set_current(-1)

    def test_set_over(self):
        # assemble
        with HCS3202(PORT, max_current=1) as device:
            # act & assert
            with pytest.raises(AssertionError, match=r"^Invalid.*"):
                result = device.set_current(90)


class TestGetter:
    def test_get_preset(self):
        # assemble
        with HCS3202(PORT) as device:
            # act
            voltage, current = device.get_preset()
        # assert no error occurs

    def test_get_display(self):
        # assemble
        with HCS3202(PORT) as device:
            # act
            voltage, current, cv = device.get_display()
        # assert no error occurs


class TestSetGet:
    def test_set_get_voltage(self):
        # assemble
        with HCS3202(PORT) as device:
            # act
            target_voltage = 12.0
            result = device.set_voltage(target_voltage)
            voltage, current = device.get_preset()
        # assert
        assert voltage == target_voltage

    def test_set_get_current(self):
        # assemble
        with HCS3202(PORT) as device:
            # act
            target_current = 0.5
            result = device.set_current(target_current)
            voltage, current = device.get_preset()
        # assert
        assert current == target_current
