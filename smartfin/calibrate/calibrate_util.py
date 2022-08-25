import serial
import sys
from datetime import date
import time
import pandas as pd
import numpy as np
from argparse import ArgumentParser
import json
import struct

from sklearn import linear_model
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading

import sys
sys.path.append("../")
from cli_util import drop_into_cli

import logging
logging_fmt = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.INFO, format=logging_fmt)

DATA_COLUMNS = ["time", "xAcc", "yAcc", "zAcc", "xAng", "yAng", "zAng", "xMag", "yMag", "zMag", "temp", "water", "lat", "lon"]

ACC_COLS = ["xAcc", "yAcc", "zAcc"]
GYRO_COLS = ["xAng", "yAng", "zAng"]
MAG_COLS = ["xMag", "yMag", "zMag"]
THERMAL_COLS = ["temp"]

class data_input_thread(threading.Thread):
    def __init__(self, threadID, port, run_event, df_data, period):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.port = port
        self.run_event = run_event
        self.df_data = df_data
        self.period = period
        
        drop_into_cli(port) #drops into CLI mode
        port.write(('*\r').encode()) #enters developer mode
        port.write(('4\r').encode()) #executes monitor sensor

    def run(self):
        logging.info("Starting thread {}".format(self.threadID))
        monitor_sensors(self.port, self.df_data, self.run_event, self.period)
        logging.info("Exiting thread {}".format(self.threadID))
        exit_monitor_sensors(self.port)

def monitor_sensors(port: serial.Serial, df_data, run_event, period):
    start_time = None
    while run_event.is_set():
        data = port.read_until("\r".encode()).decode(errors='ignore')
        parsed_data = np.fromstring(data, dtype=float, sep='\t')

        if (parsed_data.size == len(DATA_COLUMNS)):
            if not start_time:
                start_time = time.time()
                logging.info(start_time)
            elif period and time.time() - start_time >= period:
                run_event.clear()
                break

            logging.debug(parsed_data)
            df_data.loc[df_data.shape[0],:] = parsed_data

def exit_monitor_sensors(port):
    port.write(chr(27).encode()) #exits monitor sensors
    while True:
        data = port.readline().decode(errors='ignore')
        if (data == "Exit complete\n"):
            break
        port.write('X\r'.encode()) #Exits CLI Mode

def split_data(df, cols):
    return [df.loc[:,col] for col in cols]

def axis_to_idx(axis):
    if (axis == "x"):
        return 0
    if (axis == "y"):
        return 1
    if (axis == "z"):
        return 2
    return None


def plot_magnetometer_3D(df, title=None, real_time=True):
    x, y, z = tuple(split_data(df, ["xMag", "yMag", "zMag"]))

    ax = plt.axes(projection='3d')

    ax.plot(x, y, z, '.b')
    ax.set_xlabel('$\mu$T')
    ax.set_ylabel('$\mu$T')
    ax.set_zlabel('$\mu$T')
    if title:
        plt.title(title)

    if real_time:
        plt.pause(0.001)
    else:
        plt.show()

def plot_magnetometer_2D(df, title=None, real_time=True):
    x, y, z = tuple(split_data(df, ["xMag", "yMag", "zMag"]))

    plt.scatter(x, y, c='blue', label='xy')
    plt.scatter(y, z, c='red', label='yz')
    plt.scatter(z, x, c='green', label='zx')
    plt.xlabel('$\mu$T')
    plt.ylabel('$\mu$T')
    plt.grid(True)
    if title:
        plt.title(title)
        
    if real_time:
        plt.pause(0.001)
    else:
        plt.show()

def plot_time_series(df, cols, ylim=None, xlim = None, title=None):
    data = split_data(df, ["time"] + cols)
    fig, axis = plt.subplots(1, 3, figsize=(12,4))
    
    x = data[0]
    Y = data[1:]
    if len(x) != 0:
        start_time = x[0]
        for ax, y in zip(axis, Y):
            ax.scatter(x-start_time, y)
            if ylim:
                ax.set_ylim(bottom=ylim[0], top=ylim[1])

    plt.pause(0.001)
    plt.close(fig)
    
def plot_accelerometer(df):
    plot_time_series(df, ["xAcc", "yAcc", "zAcc"], ylim=(-2, 2))
    
def plot_gyroscope(df):
    plot_time_series(df, ["xAng", "yAng", "zAng"])
    
def save_to_csv(df, fields, fp):
    df.loc[:,fields].to_csv(fp, index=False, header=False)
    
def data_input_main(port_p, plotter, period=None):
    run_event = threading.Event()
    run_event.set()
    
    df_data = pd.DataFrame(columns=DATA_COLUMNS)
    with serial.Serial(port=port_p, baudrate=115200) as port:
        port.timeout = 1
        data_thread = data_input_thread(1, port, run_event, df_data, period)
        
        data_thread.start()
        try:
            while run_event.is_set():
                if plotter:
                    plotter(df_data)
                time.sleep(.1)
        finally:
            logging.info("Closing threads")
            run_event.clear()
            data_thread.join()
            logging.info("Threads successfully closed")
            logging.debug(df_data)
            return df_data

def load_cal(input_dir):
    with open(input_dir, 'r') as json_file:
        prev_cal_data = json.load(json_file)
        
    return prev_cal_data

def save_cal(output_dir, cal_type, cal_data):
    if isinstance(cal_data, np.ndarray):
        cal_data = arr_to_csv_str(cal_data)
    
    try:
        prev_cal_data = load_cal(output_dir)
    except FileNotFoundError:
        prev_cal_data = {}
    prev_cal_data[cal_type] = cal_data
    
    with open(output_dir, 'w') as json_file:
        json.dump(prev_cal_data, json_file)

def arr_to_csv_str(arr):
    return "\n".join([",".join([str(element) for element in row]) if arr.ndim > 1 else str(row) for row in arr])

def csv_str_to_arr(csv_str):
    return np.array([[float(element) for element in row.split(",")] for row in csv_str.split('\n')])

def float_to_bin(num):
    return format(struct.unpack('!I', struct.pack('!f', num))[0], '032b')

def bin_to_float(binary):
    return struct.unpack('!f',struct.pack('!I', int(binary, 2)))[0]

def calibrate_main_sensor(sensor_name, sensor_cols, cal_data_dict, df_data):
    coeff_key = "{}_coeff".format(sensor_name)
    intercept_key = "{}_intercept".format(sensor_name)
    if coeff_key not in cal_data_dict and intercept_key not in cal_data_dict:
        return None
    
    mod = linear_model.LinearRegression()
    if coeff_key not in cal_data_dict:
        mod.coef_ = np.identity(len(sensor_cols))
    else:
        mod.coef_ = csv_str_to_arr(cal_data_dict[coeff_key])
    mod.intercept_ = csv_str_to_arr(cal_data_dict[intercept_key]).flatten() #might not work because all arrays are 2D
    
    df_uncal_data = df_data.loc[:,sensor_cols]
    nan_msk = ~df_data.loc[:,sensor_cols].isna().any(axis=1)
    
    #performs prediction
    yhat = np.full(df_uncal_data.shape, np.nan)
    pred = mod.predict(df_uncal_data[nan_msk].to_numpy())
    yhat[nan_msk.astype(bool), ...] = pred
    
    #inserts columns in original dataframe
    df_data.loc[:,sensor_cols] = yhat
