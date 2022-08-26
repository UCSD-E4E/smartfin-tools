import pandas as pd
import numpy as np
from argparse import ArgumentParser
import logging as logger

from scipy import linalg
import math

from calibrate_util import *

MFIELD = 300

def ellipsoid_fit(s):
    ''' Estimate ellipsoid parameters from a set of points.
        Parameters
        ----------
        s : array_like
          The samples (M,N) where M=3 (x,y,z) and N=number of samples.
        Returns
        -------
        M, n, d : array_like, array_like, float
          The ellipsoid parameters M, n, d.
        References
        ----------
        .. [1] Qingde Li; Griffiths, J.G., "Least squares ellipsoid specific
           fitting," in Geometric Modeling and Processing, 2004.
           Proceedings, vol., no., pp.335-340, 2004
    '''

    # D (samples)
    D = np.array([s[0]**2., s[1]**2., s[2]**2.,
                  2.*s[1]*s[2], 2.*s[0]*s[2], 2.*s[0]*s[1],
                  2.*s[0], 2.*s[1], 2.*s[2], np.ones_like(s[0])])

    # S, S_11, S_12, S_21, S_22 (eq. 11)
    S = np.dot(D, D.T)
    S_11 = S[:6,:6]
    S_12 = S[:6,6:]
    S_21 = S[6:,:6]
    S_22 = S[6:,6:]

    # C (Eq. 8, k=4)
    C = np.array([[-1,  1,  1,  0,  0,  0],
                  [ 1, -1,  1,  0,  0,  0],
                  [ 1,  1, -1,  0,  0,  0],
                  [ 0,  0,  0, -4,  0,  0],
                  [ 0,  0,  0,  0, -4,  0],
                  [ 0,  0,  0,  0,  0, -4]])

    # v_1 (eq. 15, solution)
    E = np.dot(linalg.inv(C),
               S_11 - np.dot(S_12, np.dot(linalg.inv(S_22), S_21)))

    E_w, E_v = np.linalg.eig(E)

    v_1 = E_v[:, np.argmax(E_w)]
    if v_1[0] < 0: v_1 = -v_1

    # v_2 (eq. 13, solution)
    v_2 = np.dot(np.dot(-np.linalg.inv(S_22), S_21), v_1)

    # quadric-form parameters
    M = np.array([[v_1[0], v_1[3], v_1[4]],
                  [v_1[3], v_1[1], v_1[5]],
                  [v_1[4], v_1[5], v_1[2]]])
    n = np.array([[v_2[0]],
                  [v_2[1]],
                  [v_2[2]]])
    d = v_2[3]

    return M, n, d

def createMatrices(df, mag_field):
    data_arr = df.to_numpy()

    # ellipsoid fit
    s = np.array(data_arr).T
    M, n, d = ellipsoid_fit(s)

    # calibration parameters
    M_1 = linalg.inv(M)
    b = -np.dot(M_1, n)
    A_1 = np.real(mag_field / np.sqrt(np.dot(n.T, np.dot(M_1, n)) - d) * linalg.sqrtm(M))
    
    return A_1, b

def cal_mag_main(port_p):
    df = data_input_main(port_p, plot_magnetometer_3D).loc[:,MAG_COLS].dropna().astype(np.float) #real time input
    hard_iron, soft_iron = createMatrices(df, MFIELD)
    
    coef_ = hard_iron
    intercept_ = np.matmul(hard_iron, -1*soft_iron)
    
    logger.info("coefficient:\n{}".format(coef_))
    logger.info("intercept:\n{}".format(intercept_))
    
    df_cal = df.copy()
    calibrate_main_sensor("mag", MAG_COLS, {"mag_coeff": arr_to_csv_str(coef_), "mag_intercept":arr_to_csv_str(intercept_)}, df_cal)
    
    plot_magnetometer_3D(df, "Uncalibrated 3D", real_time=False)
    plot_magnetometer_2D(df, "Uncalibrated 2D", real_time=False)
    plot_magnetometer_3D(df_cal, "Calibrated 3D", real_time=False)
    plot_magnetometer_2D(df_cal, "Calibrated 2D", real_time=False)
    
    logger.info(df.head())
    logger.info(df_cal.head())

    return coef_, intercept_
    
def main():
    parser = ArgumentParser()
    parser.add_argument("port", help="path to serial port of fin")
    parser.add_argument('--output_dir', '-o', default="calibrations.json", help="json file to output calibration coefficients to (default: calibrations.json)")

    args = parser.parse_args()
    output_dir = args.output_dir
    
    coef_, intercept_ = cal_mag_main(args.port)
    save_cal(output_dir, "mag_coeff", coef_)
    save_cal(output_dir, "mag_intercept", intercept_)

    
if __name__ == "__main__":
    main()