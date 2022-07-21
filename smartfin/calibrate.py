import serial
import sys
from datetime import date
import time
import pandas as pd
import numpy as np
from argparse import ArgumentParser
from cli_util import drop_into_cli

import matplotlib.pyplot as plt

DATA_COLUMNS = ["time", "xAcc", "yAcc", "zAcc", "xAng", "yAng", "zAng", "xMag", "yMag", "zMag", "temp", "water", "lat", "lon"]


def monitor_sensors(port: serial.Serial):
    port.write(('*\r').encode()) #enters developer mode
    port.write(('4\r').encode()) #executes monitor sensor
    
    df_data = pd.DataFrame(columns=DATA_COLUMNS)
    while True:
        try:
            data = port.readline().decode(errors='ignore')
            parsed_data = np.fromstring(data, dtype=float, sep='\t')
            
            if (parsed_data.size == len(DATA_COLUMNS)):
                print(parsed_data)
                df_data.loc[df_data.shape[0],:] = parsed_data
                real_time_plot(df_data.loc[:, "time"].values, df_data.loc[:, "temp"].values)
                
        except:
            port.write(chr(27).encode()) #exits monitor sensors
            while True:
                data = port.readline().decode(errors='ignore')
                if (data == "Exit complete\n"):
                    break;
                port.write('X\r'.encode()) #Exits CLI Mode
            break;
        
    return df_data

def real_time_plot(x, y):
    plt.scatter(x, y, c="blue")
    plt.pause(0.05)

def csvToPd():
    df = pd.read_csv('1658269077.csv')
    print(df)

    print(df['    xMag'].astype(str) + ',' + df['    yMag'].astype(str) + ',' + df['    yMag'].astype(str))

def main():
    parser = ArgumentParser()
    parser.add_argument("port")
    parser.add_argument('--output_dir', '-o', default='.')

    args = parser.parse_args()

    with serial.Serial(port=args.port, baudrate=115200) as port:
        port.timeout = 1
        drop_into_cli(port)
        monitor_sensors(port)
    
if __name__ == "__main__":
    main()