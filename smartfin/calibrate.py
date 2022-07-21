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
                plot_magnetometer_3D(df_data, "3D Magentometer Data")
                
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
    
def plot_magnetometer_3D(df, title=None):
    x = df.loc[:,"xMag"]
    y = df.loc[:,"yMag"]
    z = df.loc[:,"xMag"]

    ax = plt.axes(projection='3d')

    ax.plot(x, y, z, '.b')
    ax.set_xlabel('$\mu$T')
    ax.set_ylabel('$\mu$T')
    ax.set_zlabel('$\mu$T')
    if title:
        plt.title(title)

    #plt.pause(0.001)

def plot_magnetometer(self, data, title=None):
    x, y, z = self.split(data)
    plt.plot(x, y, '.b', x, z, '.r', z, y, '.g')
    plt.xlabel('$\mu$T')
    plt.ylabel('$\mu$T')
    plt.grid(True)
    if title:
        plt.title(title)

    plt.savefig(str(self.plot_count) + '.png')
    self.plot_count += 1

def save_to_csv(df, fields, fp):
    df.loc[:,fields].to_csv(fp)

def main():
    parser = ArgumentParser()
    parser.add_argument("port")
    parser.add_argument('--output_dir', '-o', default='.')

    args = parser.parse_args()

    with serial.Serial(port=args.port, baudrate=115200) as port:
        port.timeout = 1
        drop_into_cli(port)
        df_data = monitor_sensors(port)
        
    #save_to_csv(df_data, ["xMag", "yMag", "zMag"], "data.csv")
    
if __name__ == "__main__":
    main()