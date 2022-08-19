import pandas as pd
import numpy as np
from argparse import ArgumentParser
import logging as logger

from calibrate_util import *

def cal_mag_main(port_p):
    df = data_input_main(port_p, plot_magnetometer_3D)
    
def main():
    parser = ArgumentParser()
    parser.add_argument("port")
    parser.add_argument('--output_dir', '-o', default="calibrations.json")

    args = parser.parse_args()
    output_dir = args.output_dir
    
    coef_, intercept_ = cal_mag_main(args.port)
    save_cal(output_dir, "mag_coeff", coef_)
    save_cal(output_dir, "mag_intercept", intercept_)