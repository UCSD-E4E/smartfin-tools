'''Tests decoding
'''
import struct

from hypothesis import given
from hypothesis import strategies as st

from smartfin_tools.decoder import decode_packet


@given(st.floats(min_value=5, max_value=40),
       st.booleans(),
       st.integers(min_value=0, max_value=0xfffff))
def test_temperature(temp: float, water: bool, timestamp: int):
    """Test temperature

    Args:
        temp (float): Temperature
        water (bool): Water
        timestamp (int): Timestamp (decisecond)
    """
    data_time_byte = ((timestamp & 0x000F0000) >> 12) | 0x01
    time_msb = timestamp & 0xFFFF
    blob = struct.pack('<BHhb', data_time_byte,
                       time_msb, int(temp * 128), int(water))
    dut = decode_packet(blob)
    assert len(dut) == 1
    ensemble = dut[0]
    assert ensemble['timestamp'] == timestamp / 10.
    assert ensemble['dataType'] == 1
    assert abs(ensemble['temp'] / 128. - temp) < 0.01
    assert ensemble['water'] == water
