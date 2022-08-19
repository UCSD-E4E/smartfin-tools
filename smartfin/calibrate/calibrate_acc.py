import pandas as pd
import numpy as np
from argparse import ArgumentParser
import json
import logging as logger

from sklearn import linear_model

from calibrate_util import *

DEFAULT_CAL_PERIOD = 10
axii = ["+x", "-x", "+y", "-y", "+z", "-z"]
ACC_COLS = ["xAcc", "yAcc", "zAcc"]

def cal_get_uncald_vec(port_p, axis_name, cols, vec_dict, plotter, period):
    df = data_input_main(port_p, plotter, period=period)
    df_cols = df.loc[:,cols]
    vec_dict[axis_name] = np.asarray(df_cols.mean())
    
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

def cal_acc_main(port_p, cal_period):
    uncald_vecs = {}
    for axis in axii:
        print("Please place fin so gravity is in the {} orientation".format(axis))
        print("Press enter to start data collection")
        input()
        cal_get_uncald_vec(port_p, axis, ACC_COLS, uncald_vecs, plot_accelerometer, cal_period)
    
    X, y = cal_prep_acc_data(uncald_vecs)
    logger.debug("X: {}".format(X))
    logger.debug("y: {}".format(y))
    
    mod = linear_model.LinearRegression()
    mod.fit(X, y)
    logger.info("coef: {}".format(mod.coef_))
    logger.info("intercept: {}".format(mod.intercept_))
    
    return mod.coef_, mod.intercept_, mod

def main():
    parser = ArgumentParser()
    parser.add_argument("port")
    parser.add_argument('--output_dir', '-o', default="calibrations.json")
    parser.add_argument('--cal_per', '-p', default=DEFAULT_CAL_PERIOD)

    args = parser.parse_args()
    output_dir = args.output_dir

    coef_, intercept_, = cal_acc_main(args.port, args.cal_per)
    save_cal(output_dir, "acc_coeff", coef_)
    save_cal(output_dir, "acc_intercept", intercept_)
    

if __name__ == "__main__":
    main()