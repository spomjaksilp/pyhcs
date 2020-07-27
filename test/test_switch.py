import pytest

from hcs import HCS3202

PORT = "/dev/ttyUSB0"


class TestSwitch:
    @pytest.mark.parametrize("output", [False, True])
    def test_set_output(self, output):
        # assemble
        with HCS3202(PORT) as device:
            # act
            result = device.set_output(output)
        # assert
        assert result

    def test_enable(self):
        # assemble
        with HCS3202(PORT) as device:
            # act
            result = device.enable()
        # assert
        assert result

    def test_disable(self):
        # assemble
        with HCS3202(PORT) as device:
            # act
            result = device.disable()
        # assert
        assert result