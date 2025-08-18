'''Record decoder
'''
import logging
import struct
from typing import Callable, Dict, List, Tuple, Union

import pandas as pd

__parserTable = {
    1: {
        'fmt': '<hb',
        'names': ['temp', 'water']
    },
    2: {
        'fmt': '<bbb',
        'names': ['rawXAcc', 'rawYAcc', 'rawZAcc']
    },
    3: {
        'fmt': '',
        'names': []
    },
    4: {
        'fmt': '<hbbbb',
        'names': ['temp', 'water', 'rawXAcc', 'rawYAcc', 'rawZAcc']
    },
    5: {
        'fmt': '',
        'names': []
    },
    6: {
        'fmt': '<hbbbbii',
        'names': ['temp', 'water', 'rawXAcc', 'rawYAcc', 'rawZAcc', 'lat', 'lon']
    },
    7: {
        'fmt': '<H',
        'names': ['battery']
    },
    8: {
        'fmt': '<hbI',
        'names': ['temp', 'water', 'time']
    },
    9: {
        'fmt': '<hhhhhhhhh',
        'names': ['xAcc', 'yAcc', 'zAcc', 'xGyro', 'yGyro', 'zGyro', 'xMag', 'yMag', 'zMag']
    },
    10: {
        'fmt': '<hbhhhhhhhhh',
        'names': ['temp', 'water', 'xAcc', 'yAcc', 'zAcc', 'xGyro', 'yGyro',
                  'zGyro', 'xMag', 'yMag', 'zMag']
    },
    11: {
        'fmt': '<hbhhhhhhhhhii',
        'names': ['temp', 'water', 'xAcc', 'yAcc', 'zAcc', 'xGyro', 'yGyro',
                  'zGyro', 'xMag', 'yMag', 'zMag', 'lat', 'lon']
    },
    0x0C: {
        'fmt': '<hhhhhhhhh',
        'names': ['xAccQ10', 'yAccQ10', 'zAccQ10', 'xAngQ7', 'yAngQ7', 'zAngQ7',
                  'xMagQ3', 'yMagQ3', 'zMagQ3']
    }
}


def strip_padding(packet: bytes) -> bytes:
    """Strips any padding from the packet.

    This padding is defined to be any bytes after the end of valid ensembles. Do
    not run this on packets with bridged ensembles (i.e. ensembles that cross
    packet boundaries)

    Args:
        packet (bytes): Binary packet blob of multiple ensembles

    Returns:
        bytes: Stripped packet of ensembles
    """
    logger = logging.getLogger('Smartfin Decoder')
    stripped_data = b''
    idx = 0
    while idx < len(packet):
        start_idx = idx
        if len(packet) - idx < 3:
            break
        datetime_byte = packet[idx]
        idx += 1
        # time_msb: int = struct.unpack('<H', packet[idx:idx + 2])[0]
        idx += 2
        # time_ds = ((datetime_byte & 0xF0) >> 4) | (time_msb << 4)
        data_type = datetime_byte & 0x0F
        if data_type in __parserTable:
            # can use from parser table
            parse_params = __parserTable[data_type]
            expected_len = struct.calcsize(parse_params['fmt'])
            idx += expected_len
            stripped_data += packet[start_idx:idx]
        elif data_type == 0:
            # Padding
            logger.warning('Unknown data type: 0 at index %d', idx)
            stripped_data += packet[start_idx:idx-3]
            return stripped_data
        elif data_type == 0x0F:
            # text
            text_len = packet[idx]
            idx += 1
            idx += text_len
            stripped_data += packet[start_idx:idx]
        else:
            logger.warning('Unknown data type: %d', data_type)
    return stripped_data


def decode_packet(packet: bytes) -> List[Dict[str, Union[int, float]]]:
    """Decodes a packet of ensembles into a list of dicts (one per ensemble)

    Args:
        packet (bytes): Packet of binary ensembles

    Returns:
        List[Dict[str, Union[int, float]]]: List of data blobs
    """
    logger = logging.getLogger("Smartfin Decoder")
    packet_list = []
    blob_list: List[bytes] = []
    packet_counter = 0
    idx = 0
    start_idx = 0
    while idx < len(packet):
        start_idx = idx
        if len(packet) - idx < 3:
            break
        next_candidate = packet[idx:]
        timestamp, data_type = extract_header(next_candidate)
        idx += 3
        if data_type in __parserTable:
            # can use from parser table
            parse_params = __parserTable[data_type]
            expected_len = struct.calcsize(parse_params['fmt'])
            assert len(packet) - idx >= expected_len
            ens_payload = packet[idx:idx + expected_len]
            idx += expected_len
            ens_fields = struct.unpack(parse_params['fmt'], ens_payload)
            ensemble = {}
            assert (len(parse_params['names']) == len(ens_fields))
            for i in range(len(parse_params['names'])):
                ensemble[parse_params['names'][i]] = ens_fields[i]
            ensemble['timestamp'] = timestamp
            ensemble['dataType'] = data_type
            packet_list.append(ensemble)
            binary_ensemble = packet[start_idx:idx]
            blob_list.append(binary_ensemble)
            packet_counter += 1
        elif data_type == 0:
            # Padding
            # logger.warning('Unknown data type: 0 at index %d', idx)
            idx -= 2
            continue
        elif data_type == 0x0F:
            # text
            text_len = packet[idx]
            assert len(packet) - idx >= text_len
            idx += 1
            text = packet[idx:idx + text_len].decode()
            idx += text_len
            ensemble = {}
            ensemble['text'] = text
            ensemble['timestamp'] = timestamp
            ensemble['dataType'] = data_type
            packet_list.append(ensemble)
            blob_list.append(packet[start_idx:idx])
            packet_counter += 1
        else:
            logger.warning('Unknown data type: %d', data_type)
    return packet_list


def extract_header(packet: bytes) -> Tuple[float, int]:
    """Extracts the next packet header.  Always consumes 3 bytes

    Args:
        packet (bytes): Binary blob

    Returns:
        Tuple[float, int]: timestamp (ds), data type
    """
    datetime_byte = packet[0]
    time_msb: int = struct.unpack("<H", packet[1:3])[0]
    time_ds = ((datetime_byte & 0xF0) >> 4) | (time_msb << 4)
    timestamp = time_ds / 10.
    data_type = datetime_byte & 0x0F
    return timestamp, data_type


si_conversions: Dict[str, Tuple[str, Callable]] = {
    'timestamp': ('Timestamp (s)', lambda x: x),
    'temp': ('Temperature (C)', lambda x: x / 128),
    'water': ('Water Detect', lambda x: x > 0),
    'xAcc': ('X Acceleration (m/s^2)', lambda x: x / 16384),
    'yAcc': ('Y Acceleration (m/s^2)', lambda x: x / 16384),
    'zAcc': ('Z Acceleration (m/s^2)', lambda x: x / 16384),
    'xGyro': ('X Angular Velocity (deg/s)', lambda x: x / 131.072),
    'yGyro': ('Y Angular Velocity (deg/s)', lambda x: x / 131.072),
    'zGyro': ('Z Angular Velocity (deg/s)', lambda x: x / 131.072),
    'xMag': ('X Magnetic Field (uT)', lambda x: x * 0.15),
    'yMag': ('Y Magnetic Field (uT)', lambda x: x * 0.15),
    'zMag': ('Z Magnetic Field (uT)', lambda x: x * 0.15),
    'xAccQ10': ('X Acceleration (m/s^2)', lambda x: x / 1024),
    'yAccQ10': ('Y Acceleration (m/s^2)', lambda x: x / 1024),
    'zAccQ10': ('Z Acceleration (m/s^2)', lambda x: x / 1024),
    'xGyroQ7': ('X Angular Velocity (deg/s)', lambda x: x / 128),
    'yGyroQ7': ('Y Angular Velocity (deg/s)', lambda x: x / 128),
    'zGyroQ7': ('Z Angular Velocity (deg/s)', lambda x: x / 128),
    'xMagQ3': ('X Magnetic Field (uT)', lambda x: x / 8),
    'yMagQ3': ('Y Magnetic Field (uT)', lambda x: x / 8),
    'zMagQ3': ('Z Magnetic Field (uT)', lambda x: x / 8),
}

def convert_to_si(df: pd.DataFrame) -> pd.DataFrame:
    """Converts columns to SI units

    Args:
        df (pd.DataFrame): Raw column dataframe

    Returns:
        pd.DataFrame: SI Columned dataframe
    """
    columns = df.columns.to_list()
    for col in columns:
        if col not in si_conversions:
            continue
        mapping = si_conversions[col]
        df[mapping[0]] = mapping[1](df[col])
    return df
