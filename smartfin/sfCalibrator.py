import pandas as pd
import numpy as np
from argparse import ArgumentParser
import json

from sklearn import linear_model
import matplotlib.pyplot as plt

from cli_util import drop_into_cli

from calibrate.calibrate_util import *

import logging as logger
logging_fmt = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.INFO, format=logging_fmt)

ACC_COLS_SI = ["X Acceleration", "Y Acceleration", "Z Acceleration"]
GYRO_COLS_SI = ["X Angular Velocity", "Y Angular Velocity", "Z Angular Velocity"]
MAG_COLS_SI = ["X Angular Velocity", "Y Angular Velocity", "Z Angular Velocity"]
THERMAL_COLS_SI = ["Temperature"]

SENSORS = {"gyro": GYRO_COLS_SI, "acc": ACC_COLS_SI, "mag": MAG_COLS_SI, "thermal": THERMAL_COLS_SI}
CAL_COEFFS = ["gyro_intercept", "acc_coeff", "acc_intercept", "mag_coeff", "mag_intercept", "thermal_coeff", "thermal_intercept"]

def calibrate_main(input_dir, df_data):
    cal_data_dict = load_cal(input_dir)
    
    for sensor in SENSORS:
        calibrate_main_sensor(sensor, SENSORS[sensor], cal_data_dict, df_data)

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
    
def main():
    parser = ArgumentParser()
    parser.add_argument("data_fp")
    parser.add_argument("coef_fp")

    args = parser.parse_args()
    
    df_data = pd.read_csv(args.data_fp)
    calibrate_main(args.coef_fp, df_data)
    
    logger.info(df_data.head())
    
if __name__ == "__main__":
    main()
    
    