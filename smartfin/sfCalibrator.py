import pandas as pd
import numpy as np
from argparse import ArgumentParser
import json
import os

from cli_util import drop_into_cli

from calibrate.calibrate_util import *

import logging as logger
logging_fmt = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.INFO, format=logging_fmt)

ACC_COLS_SI = ["X Acceleration", "Y Acceleration", "Z Acceleration"]
GYRO_COLS_SI = ["X Angular Velocity", "Y Angular Velocity", "Z Angular Velocity"]
MAG_COLS_SI = ["X Magnetic Field", "Y Magnetic Field", "Z Magnetic Field"]
THERMAL_COLS_SI = ["Temperature"]

SENSORS = {"gyro": GYRO_COLS_SI, "acc": ACC_COLS_SI, "mag": MAG_COLS_SI, "thermal": THERMAL_COLS_SI}
CAL_COEFFS = ["gyro_intercept", "acc_coeff", "acc_intercept", "mag_coeff", "mag_intercept", "thermal_coeff", "thermal_intercept"]

def calibrate_main(input_dir, df_data):
    cal_data_dict = load_cal(input_dir)
    
    for sensor in SENSORS:
        calibrate_main_sensor(sensor, SENSORS[sensor], cal_data_dict, df_data)
    
def main():
    parser = ArgumentParser()
    parser.add_argument("data_fp", help="filepath to csv datafile")
    parser.add_argument("coef_fp", help="filepath to json coefficients file")
    parser.add_argument("--output_dir", "-o", default=None, help="output directory to save calibrated data to (default: {data_filename}_cal.csv)")

    args = parser.parse_args()
    
    df_data = pd.read_csv(args.data_fp)
    calibrate_main(args.coef_fp, df_data)
    
    output_dir = args.output_dir
    if not output_dir:
        filename, file_ext = os.path.splitext(args.data_fp)
        output_dir = "{}_cal{}".format(filename, file_ext)
        
    df_data.to_csv(output_dir, index=False) 
    
if __name__ == "__main__":
    main()
