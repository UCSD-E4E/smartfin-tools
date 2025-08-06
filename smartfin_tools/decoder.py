'''Record decoder
'''
import base64
import logging
import struct
from typing import Callable, Dict, List, Union

import pandas as pd


def decode_record(record: str,
                 *,
                 decoder: Callable[[str], bytes] = base64.urlsafe_b64decode
                 ) -> List[Dict[str, Union[int, float]]]:
    """Decodes ASCII encoded record of packets to list of data ensembles

    Args:
        record (str): ASCII Encoded data ensembles
        decoder (Callable[[str], bytes], optional): ASCII decoder function. 
        Defaults to base64.urlsafe_b64decode.

    Returns:
        List[Dict[str, Union[int, float]]]: List of data ensembles
    """
    packet = decoder(record)
    return decode_packet(packet)


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
        'names': ['xAcc', 'yAcc', 'zAcc', 'xAng', 'yAng', 'zAng', 'xMag', 'yMag', 'zMag']
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
    idx = 0
    while idx < len(packet):
        if len(packet) - idx < 3:
            break
        datetime_byte = packet[idx]
        idx += 1
        time_msb: int = struct.unpack("<H", packet[idx:idx + 2])[0]
        idx += 2
        time_ds = ((datetime_byte & 0xF0) << 12) | time_msb
        timestamp = time_ds / 10.
        data_type = datetime_byte & 0x0F
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
        elif data_type == 0:
            # Padding
            logger.warning('Unknown data type: 0 at index %d', idx)
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
        else:
            logger.warning('Unknown data type: %d', data_type)
    return packet_list


def convert_to_si(df: pd.DataFrame) -> pd.DataFrame:
    """Converts columns to SI units

    Args:
        df (pd.DataFrame): Raw column dataframe

    Returns:
        pd.DataFrame: SI Columned dataframe
    """
    if 'temp' in df.columns:
        df['Temperature'] = df['temp'] / 128
    if 'water' in df.columns:
        df['Water Detect'] = df['water'].astype(bool)
    if 'xAcc' in df.columns:
        df['X Acceleration'] = df['xAcc'] / 16384
    if 'yAcc' in df.columns:
        df['Y Acceleration'] = df['yAcc'] / 16384
    if 'zAcc' in df.columns:
        df['Z Acceleration'] = df['zAcc'] / 16384
    if 'xGyro' in df.columns:
        df['X Angular Velocity'] = df['xGyro'] / 131.072
    if 'yGyro' in df.columns:
        df['Y Angular Velocity'] = df['yGyro'] / 131.072
    if 'zGyro' in df.columns:
        df['Z Angular Velocity'] = df['zGyro'] / 131.072
    if 'xMag' in df.columns:
        df['X Magnetic Field'] = df['xMag'] * 0.15
    if 'yMag' in df.columns:
        df['Y Magnetic Field'] = df['yMag'] * 0.15
    if 'zMag' in df.columns:
        df['Z Magnetic Field'] = df['zMag'] * 0.15
    return df
