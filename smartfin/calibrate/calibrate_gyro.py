import pandas as pd
import numpy as np
from argparse import ArgumentParser
import logging as logger

from calibrate_util import *
logging_fmt = '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
logging.basicConfig(level=logging.INFO, format=logging_fmt)

DEFAULT_CAL_PERIOD = 60

def cal_gyro_main(port_p, period=60):
    df = data_input_main(port_p, plot_gyroscope, period=period)
    df_gyroscope = df.loc[:,GYRO_COLS]
    
    df_cal = df_gyroscope.mean() * -1
    logger.info("Calibration offsets: {}".format(df_cal.to_numpy()))
    return df_cal.to_numpy()

def main():
    parser = ArgumentParser()
    parser.add_argument("port")
    parser.add_argument('--output_dir', '-o', default="calibrations.json")
    parser.add_argument('--cal_per', '-p', default=DEFAULT_CAL_PERIOD)

    args = parser.parse_args()
    output_dir = args.output_dir

    save_cal(output_dir, "gyro_intercept", cal_gyro_main(args.port, float(args.cal_per)))
    