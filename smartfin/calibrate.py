import pandas as pd
import numpy as np
from argparse import ArgumentParser
import json
import ctypes

from sklearn import linear_model
from scipy import integrate
import matplotlib.pyplot as plt

from cli_util import drop_into_cli

from calibrate_util import *

import logging
logging_fmt = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.INFO, format=logging_fmt)

axii = ["+x", "-x", "+y", "-y", "+z", "-z"]
CAL_PERIOD = 10
CAL_VAL_FREQ = 5

ACC_COLS = ["xAcc", "yAcc", "zAcc"]
GYRO_COLS = ["xAng", "yAng", "zAng"]
MAG_COLS = ["xMag", "yMag", "zMag"]

ACC_COLS_SI = ["X Acceleration", "Y Acceleration", "Z Acceleration"]
GYRO_COLS_SI = ["X Angular Velocity", "Y Angular Velocity", "Z Angular Velocity"]
MAG_COLS_SI = ["X Angular Velocity", "Y Angular Velocity", "Z Angular Velocity"]
THERMAL_COLS_SI = ["Temperature"]

THERMAL_COLS = ["temp"]

SENSORS = {"gyro": GYRO_COLS_SI, "acc": ACC_COLS_SI, "mag": MAG_COLS_SI, "thermal": THERMAL_COLS_SI}

CAL_COEFFS = ["gyro_intercept", "acc_coeff", "acc_intercept", "mag_coeff", "mag_intercept", "thermal_coeff", "thermal_intercept"]

def cal_get_uncald_vec(port_p, axis_name, cols, vec_dict, plotter, period):
    df = data_input_main(port_p, plotter, period=period)
    df_cols = df.loc[:,cols]
    vec_dict[axis_name] = np.asarray(df_cols.mean())
    
def cal_gen_y_acc(axis, val):
    arr = np.zeros(3)
    arr[axis_to_idx(axis)] = val
    return arr

def cal_prep_acc_data(data):
    X = []
    y = []
    
    for key in data:
        if key[0] == "-":
            y.append(cal_gen_y_acc(key[1], -1))
        if key[0] == "+":
            y.append(cal_gen_y_acc(key[1], 1))
        X.append(data[key])
    return X, y

def cal_acc_validate(port_p, coeff_fp, intercept_fp):
    coeff_ = np.loadtxt(open(coeff_fp, "rb"), delimiter=",", skiprows=0)
    intercept_ = np.loadtxt(open(intercept_fp, "rb"), delimiter=",", skiprows=0)
    logging.info("coef: {}".format(coeff_))
    logging.info("intercept: {}".format(intercept_))

    df = data_input_main(port_p, plot_accelerometer, period=30)
    df_acc = df.loc[:,["time", "xAcc", "yAcc", "zAcc"]]
    df_acc = df_acc.rolling(10).mean().dropna()
    
    acc_arr = df_acc.loc[:,["xAcc", "yAcc", "zAcc"]].to_numpy()
    acc_arr[:,2] -= df_acc.mean().zAcc
    acc_arr[:,1] -= df_acc.mean().yAcc

    x = df_acc.loc[:,"time"].to_numpy()
    x = (x-x[0]) / 1000
    mod = linear_model.LinearRegression()
    mod.coef_ = coeff_
    mod.intercept_ = intercept_
    acc_cal = mod.predict(acc_arr)
    
    for acc_data in [acc_arr, acc_cal]:
        delta_v = integrate.cumtrapz(9.8 * acc_data[:,0], x)
        delta_v = np.insert(delta_v, 0, 0)
        delta_x = integrate.cumtrapz(delta_v, x)
        delta_x = np.insert(delta_x, 0, 0)
        logging.info("delta x: {}".format(delta_x[-1]))
    
        fig, axis = plt.subplots(1, 3, figsize=(12,4))
        axis[0].scatter(x, 9.8 * acc_data[:,0])
        axis[1].scatter(x, delta_v)
        axis[2].scatter(x, delta_x)
        plt.show()

def cal_acc_main(port_p):
    uncald_vecs = {}
    for axis in axii:
        print("Please place fin so gravity is in the {} orientation".format(axis))
        print("Press enter to start data collection")
        input()
        cal_get_uncald_vec(port_p, axis, ACC_COLS, uncald_vecs, plot_accelerometer, CAL_PERIOD)
    
    X, y = cal_prep_acc_data(uncald_vecs)
    logging.debug("X: {}".format(X))
    logging.debug("y: {}".format(y))
    
    mod = linear_model.LinearRegression()
    mod.fit(X, y)
    logging.info("coef: {}".format(mod.coef_))
    logging.info("intercept: {}".format(mod.intercept_))
    
    return mod.coef_, mod.intercept_, mod

def cal_gyro_main(port_p, period=60):
    df = data_input_main(port_p, plot_gyroscope, period=period)
    df_gyroscope = df.loc[:,GYRO_COLS]
    
    df_cal = df_gyroscope.mean() * -1
    logging.info("Calibration offsets: {}".format(df_cal.to_numpy()))
    return df_cal.to_numpy()

def apply_cal(input_dir, df_data):
    cal_data_dict = load_cal(input_dir)
    
    for sensor in SENSORS:
        apply_cal_sensor(sensor, SENSORS[sensor], cal_data_dict, df_data)
    
def apply_cal_sensor(sensor_name, sensor_cols, cal_data_dict, df_data):
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
    
def cal_board_set(port_p, input_dir):
    cal_dict_str = load_cal(input_dir)
    cal_dict_arr = {key: csv_str_to_arr(cal_dict_str[key]) for key in cal_dict_str} #all arrays are 2D
    
    cal_data = cal_dict_arr["acc_coeff"]
    cal_data = cal_data.flatten()
    logging.info(cal_data)
    
    cal_dict_arr = {key: [int(float_to_bin(element), 2) for element in cal_dict_arr[key].flatten()] for key in cal_dict_arr}
    logging.info(cal_dict_arr)
    
    #converts each float to binary then unsigned 32 bit int seperated by space
    #cal_conv = [bin_to_float((bin(int(num))[2:]).zfill(32)) for num in cal_data]
    #logging.info(cal_conv)

    logging.info("keys: {}".format(cal_dict_arr.keys()))
    with serial.Serial(port=port_p, baudrate=115200) as port:
        port.timeout = 1
        drop_into_cli(port)
        
        port.write('~\r'.encode())
        while True:
            line = port.readline().decode(errors='ignore').rstrip('\n')
            print(line)
            if (line == "press enter to start"):
                port.write("\r".encode())
            elif (line in CAL_COEFFS):
                cal_data = cal_dict_arr[line]
                
                for coeff_ in cal_data:
                    port.write("{}\r".format(coeff_).encode())
                    
                port.write("\r".format(coeff_).encode())
            elif (line == "Unknown command"):
                break
            else:
                continue
        port.write('X\r'.encode())
    
def main():
    parser = ArgumentParser()
    parser.add_argument("port")
    parser.add_argument('--output_dir', '-o', default=None)
    parser.add_argument('--input_dir', '-i', default=None)

    args = parser.parse_args()
    output_dir = args.output_dir

    input_dir = args.input_dir
    #coef_, intercept_, = cal_acc_main(args.port)
    
    df_data = pd.read_csv("_200047001750483553353920-20220728-201824-session-data.csv")
    apply_cal(args.input_dir, df_data)
    
    df_data.to_csv("_200047001750483553353920-20220728-201824-session-data_cal.csv", index=False)

if __name__ == "__main__":
    main()