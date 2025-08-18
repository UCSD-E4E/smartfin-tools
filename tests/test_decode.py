'''Tests decoding
'''
import struct

import numpy as np
from hypothesis import given
from hypothesis import strategies as st

from smartfin_tools.decoder import decode_packet, si_conversions


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
    data_time_byte = ((timestamp & 0x000F) << 4) | 0x01
    time_msb = timestamp >> 4
    blob = struct.pack('<BHhb', data_time_byte,
                       time_msb, int(temp * 128), int(water))
    dut = decode_packet(blob)
    assert len(dut) == 1
    ensemble = dut[0]
    assert ensemble['dataType'] == 1
    assert si_conversions['timestamp'][1](
        ensemble['timestamp']) == timestamp / 10
    ens_temp = si_conversions['temp'][1](ensemble['temp'])
    assert abs(ens_temp - temp) < 0.01
    ens_water = si_conversions['water'][1](ensemble['water'])
    assert ens_water == water


@given(
    st.floats(-31, 31),
    st.floats(-31, 31),
    st.floats(-31, 31),
    st.floats(-255, 255),
    st.floats(-255, 255),
    st.floats(-255, 255),
    st.floats(-4095, 4095),
    st.floats(-4095, 4095),
    st.floats(-4095, 4095),
    st.integers(min_value=0, max_value=0xfffff)
)
def test_hdr_imu(acc_x,
                 acc_y,
                 acc_z,
                 gyr_x,
                 gyr_y,
                 gyr_z,
                 mag_x,
                 mag_y,
                 mag_z,
                 timestamp):

    data_time_byte = ((timestamp & 0x0000000F) << 4) | 0x0c
    time_msb = timestamp >> 4
    acc_x_q10 = np.int16(acc_x * 1024)
    acc_y_q10 = np.int16(acc_y * 1024)
    acc_z_q10 = np.int16(acc_z * 1024)

    gyr_x_q7 = np.int16(gyr_x * 128)
    gyr_y_q7 = np.int16(gyr_y * 128)
    gyr_z_q7 = np.int16(gyr_z * 128)

    mag_x_q3 = np.int16(mag_x * 8)
    mag_y_q3 = np.int16(mag_y * 8)
    mag_z_q3 = np.int16(mag_z * 8)

    blob = struct.pack(
        '<BHhhhhhhhhh',
        data_time_byte,
        time_msb,
        acc_x_q10,
        acc_y_q10,
        acc_z_q10,
        gyr_x_q7,
        gyr_y_q7,
        gyr_z_q7,
        mag_x_q3,
        mag_y_q3,
        mag_z_q3,
    )
    dut = decode_packet(blob)
    assert len(dut) == 1
    ensemble = dut[0]
    assert si_conversions['timestamp'][1](
        ensemble['timestamp']) == timestamp / 10
    assert ensemble['dataType'] == 0x0c

    assert np.isclose(si_conversions['xAccQ10'][1](
        ensemble['xAccQ10']), acc_x, atol=1/1024)
    assert np.isclose(si_conversions['yAccQ10'][1](
        ensemble['yAccQ10']), acc_y, atol=1/1024)
    assert np.isclose(si_conversions['zAccQ10'][1](
        ensemble['zAccQ10']), acc_z, atol=1/1024)

    assert np.isclose(si_conversions['xGyroQ7'][1](
        ensemble['xAngQ7']), gyr_x, atol=1/128)
    assert np.isclose(si_conversions['yGyroQ7'][1](
        ensemble['yAngQ7']), gyr_y, atol=1/128)
    assert np.isclose(si_conversions['zGyroQ7'][1](
        ensemble['zAngQ7']), gyr_z, atol=1/128)

    assert np.isclose(si_conversions['xMagQ3'][1](
        ensemble['xMagQ3']), mag_x, atol=1/8)
    assert np.isclose(si_conversions['yMagQ3'][1](
        ensemble['yMagQ3']), mag_y, atol=1/8)
    assert np.isclose(si_conversions['zMagQ3'][1](
        ensemble['zMagQ3']), mag_z, atol=1/8)
