'''Record decoder
'''
import base64
import logging
import struct
from typing import Callable, Dict, List, Union

import numpy as np
import pandas as pd


def decodeRecord(record: str,
                 *,
                 decoder: Callable[[str], bytes] = base64.urlsafe_b64decode
                 ) -> List[Dict[str, Union[int, float]]]:
    packet = decoder(record)
    return decodePacket(packet)


__parserTable = {
    1: {
        'fmt': '>h',
        'len': 2,
        'names': ['temp+water']
    },
    2: {
        'fmt': '>bbb',
        'len': 3,
        'names': ['rawXAcc', 'rawYAcc', 'rawZAcc']
    },
    3: {
        'fmt': '',
        'len': 0,
        'names': []
    },
    4: {
        'fmt': '>hbbb',
        'len': 5,
        'names': ['temp+water', 'rawXAcc', 'rawYAcc', 'rawZAcc']
    },
    5: {
        'fmt': '',
        'len': 0,
        'names': []
    },
    6: {
        'fmt': '>hbbbii',
        'len': 13,
        'names': ['temp+water', 'rawXAcc', 'rawYAcc', 'rawZAcc', 'lat', 'lon']
    },
    7: {
        'fmt': '>H',
        'len': 2,
        'names': ['battery']
    },
    8: {
        'fmt': '>hI',
        'len': 6,
        'names': ['temp+water', 'time']
    },
    9: {
        'fmt': '>hhhhhhhhh',
        'len': 18,
        'names': ['xAcc', 'yAcc', 'zAcc', 'xGyro', 'yGyro', 'zGyro', 'xMag', 'yMag', 'zMag']
    },
    10: {
        'fmt': '>hhhhhhhhhh',
        'len': 20,
        'names': ['temp+water', 'xAcc', 'yAcc', 'zAcc', 'xGyro', 'yGyro', 'zGyro', 'xMag', 'yMag', 'zMag']
    },
    11: {
        'fmt': '>hhhhhhhhhhii',
        'len': 28,
        'names': ['temp+water', 'xAcc', 'yAcc', 'zAcc', 'xGyro', 'yGyro', 'zGyro', 'xMag', 'yMag', 'zMag', 'lat', 'lon']
    },
    0x0C: {
        'fmt': '>hhhhhhhhh',
        'len': 0x12,
        'names': ['xAcc', 'yAcc', 'zAcc', 'xAng', 'yAng', 'zAng', 'xMag', 'yMag', 'zMag']
    }
}


def stripPadding(packet: bytes) -> bytes:
    logger = logging.getLogger("Smartfin Decoder")
    stripped_data = b''
    idx = 0
    start_idx = 0
    while idx < len(packet):
        if len(packet) - idx < 3:
            break
        datetime_byte = packet[idx]
        idx += 1
        time_msb: int = struct.unpack("<H", packet[idx:idx + 2])[0]
        idx += 2
        time_ds = ((datetime_byte & 0xF0) >> 4) | (time_msb << 4)
        data_type = datetime_byte & 0x0F
        if data_type in __parserTable:
            # can use from parser table
            parse_params = __parserTable[data_type]
            idx += parse_params['len']
        elif data_type == 0:
            # Padding
            # logger.warning(f"Unknown data type: 0 at index {idx}")
            stripped_data += packet[start_idx:idx-3]
            idx -= 2
            start_idx = idx
            continue
        elif data_type == 0x0F:
            # text
            text_len = packet[idx]
            idx += 1
            idx += text_len
        else:
            logger.warning('Unknown data type: %d', data_type)
    return stripped_data


def decodePacket(packet: bytes) -> List[Dict[str, Union[int, float]]]:
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
        time_ds = ((datetime_byte & 0xF0) >> 4) | (time_msb << 4)
        timestamp = time_ds / 10.
        data_type = datetime_byte & 0x0F
        if data_type in __parserTable:
            # can use from parser table
            parse_params = __parserTable[data_type]
            assert len(packet) - idx >= parse_params['len']
            ens_payload = packet[idx:idx + parse_params['len']]
            idx += parse_params['len']
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
            # logger.warning(f"Unknown data type: 0 at index {idx}")
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


def convertToSI(df: pd.DataFrame) -> pd.DataFrame:
    df['Temperature'] = df['temp+water'] / 333.87 + 21.0
    water_detect = list(df['Temperature'])
    for idx, elem in enumerate(water_detect):
        if not np.isnan(elem):
            water_detect[idx] = elem >= 0
    df['Water Detect'] = water_detect
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
