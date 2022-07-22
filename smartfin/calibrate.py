import serial
import sys
from datetime import date
import time
import pandas as pd
import numpy as np
from argparse import ArgumentParser
from cli_util import drop_into_cli

import matplotlib.pyplot as plt
import threading

DATA_COLUMNS = ["time", "xAcc", "yAcc", "zAcc", "xAng", "yAng", "zAng", "xMag", "yMag", "zMag", "temp", "water", "lat", "lon"]

class data_input_thread(threading.Thread):
    def __init__(self, threadID, port, run_event, df_data):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.port = port
        self.run_event = run_event
        self.df_data = df_data
        
        drop_into_cli(port) #drops into CLI mode
        port.write(('*\r').encode()) #enters developer mode
        port.write(('4\r').encode()) #executes monitor sensor

    def run(self):
        print("Starting thread {}".format(self.threadID))
        monitor_sensors(self.port, self.df_data, self.run_event)
        print("Exiting thread {}".format(self.threadID))
        exit_monitor_sensors(self.port)

def monitor_sensors(port: serial.Serial, df_data, run_event):
    while run_event.is_set():
        try:
            data = port.readline().decode(errors='ignore')
            parsed_data = np.fromstring(data, dtype=float, sep='\t')

            if (parsed_data.size == len(DATA_COLUMNS)):
                print(parsed_data)
                df_data.loc[df_data.shape[0],:] = parsed_data
        except Exception as e:
            exit_monitor_sensors(port)
            print(e)
            break;

def exit_monitor_sensors(port):
    port.write(chr(27).encode()) #exits monitor sensors
    while True:
        data = port.readline().decode(errors='ignore')
        if (data == "Exit complete\n"):
            break;
        port.write('X\r'.encode()) #Exits CLI Mode
        
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

    plt.pause(0.001)

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
    parser.add_argument('--output_dir', '-o', default=None)

    args = parser.parse_args()
    
    run_event = threading.Event()
    run_event.set()
    
    df_data = pd.DataFrame(columns=DATA_COLUMNS)

    with serial.Serial(port=args.port, baudrate=115200) as port:
        port.timeout = 1
        data_thread = data_input_thread(1, port, run_event, df_data)
        
        data_thread.start()
        try:
            while True:
                plot_magnetometer_3D(df_data)
                time.sleep(.1)
        except:
            print("Closing threads")
            run_event.clear()
            data_thread.join()
            print("Threads successfully closed")
    
    print(df_data)
    #save_to_csv(df_data, ["xMag", "yMag", "zMag"], "data.csv")
    
if __name__ == "__main__":
    main()