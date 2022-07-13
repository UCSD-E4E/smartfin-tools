from pickle import TRUE
import struct
import base64
from typing import List
import pandas as pd
import numpy as np

LINEAR_REGRESSION_A = 1.0/126.75
LINEAR_REGRESSION_B = 0.205


def decodeRecord(record:str)->List:
    packet = base64.b85decode(record)
    return decodePacket(packet)

parserTable = {
    1:{
        'fmt': '>h',
        'len': 2,
        'names': ['temp+water']
    },
    2:{
        'fmt': '>bbb',
        'len': 3,
        'names': ['rawXAcc', 'rawYAcc', 'rawZAcc']
    },
    3:{
        'fmt': '',
        'len': 0,
        'names': []
    },
    4:{
        'fmt': '>hbbb',
        'len': 5,
        'names': ['temp+water', 'rawXAcc', 'rawYAcc', 'rawZAcc']
    },
    5:{
        'fmt': '',
        'len': 0,
        'names': []
    },
    6:{
        'fmt': '>hbbbii',
        'len': 13,
        'names': ['temp+water', 'rawXAcc', 'rawYAcc', 'rawZAcc', 'lat', 'lon']
    },
    7:{
        'fmt': '>H',
        'len': 2,
        'names': ['battery']
    },
    8:{
        'fmt': '>hI',
        'len': 6,
        'names': ['temp+water', 'time']
    },
    9:{
        'fmt': '>hhhhhhhhh',
        'len': 18,
        'names': ['xAcc', 'yAcc', 'zAcc', 'xGyro', 'yGyro', 'zGyro', 'xMag', 'yMag', 'zMag']
    },
    10:{
        'fmt': '>hhhhhhhhhh',
        'len': 20,
        'names': ['temp+water', 'xAcc', 'yAcc', 'zAcc', 'xGyro', 'yGyro', 'zGyro', 'xMag', 'yMag', 'zMag']
    },
    11:{
        'fmt': '>hhhhhhhhhhii',
        'len': 28,
        'names': ['temp+water', 'xAcc', 'yAcc', 'zAcc', 'xGyro', 'yGyro', 'zGyro', 'xMag', 'yMag', 'zMag', 'lat', 'lon']
    }
}
def decodePacket(packet:bytes)->List:
    packetList = []
    idx = 0
    while idx < len(packet):
        if len(packet) - idx < 3:
            break
        dataTimeByte = packet[idx]
        idx += 1
        timeMSB, = struct.unpack("<H", packet[idx:idx + 2])
        idx += 2
        time_ds = ((dataTimeByte & 0xF0) >> 4) | (timeMSB << 4)
        timestamp = time_ds / 10
        dataType = dataTimeByte & 0x0F
        if dataType in parserTable:
            # can use from parser table
            parseParams = parserTable[dataType]
            ensemblePayload = packet[idx:idx + parseParams['len']]
            idx += parseParams['len']
            ensembleFields = struct.unpack(parseParams['fmt'], ensemblePayload)
            ensemble = {}
            assert(len(parseParams['names']) == len(ensembleFields))
            for i in range(len(parseParams['names'])):
                ensemble[parseParams['names'][i]] = ensembleFields[i]
            ensemble['timestamp'] = timestamp
            ensemble['dataType'] = dataType
            packetList.append(ensemble)
        elif dataType == 0:
            continue
        elif dataType == 0x0F:
            # text
            textLen = packet[idx]
            assert(len(packet) - idx >= textLen)
            idx += 1
            text = packet[idx:idx + textLen].decode()
            idx += textLen
            ensemble = {}
            ensemble['text'] = text
            ensemble['timestamp'] = timestamp
            ensemble['dataType'] = dataType
            packetList.append(ensemble)
    return packetList


def convertToSI(df:pd.DataFrame):
    df['Temperature'] = df['temp+water']*LINEAR_REGRESSION_A + LINEAR_REGRESSION_B
    waterDetect = list(df['Temperature'])
    for i in range(len(waterDetect)):
        if not np.isnan(waterDetect[i]):
            if (waterDetect[i] >= 100):
                waterDetect[i] = TRUE
                df['Temperature'][i] = df['Temperature'][i] - 100
    df['Water Detect'] = waterDetect
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
    if 'lat' in df.columns:
        df['Latitude'] = df['lat'] / 1000000.0
    if 'lon' in df.columns:
        df['Longitude'] = df['lon'] / 1000000.0
        
    return df


if __name__ == "__main__":
    ensembles = []
    with open('e4e/data.txt', 'r') as dataFile:
        for line in dataFile:
            ensembles.append(decodeRecord(line.strip()))
    print(ensembles)