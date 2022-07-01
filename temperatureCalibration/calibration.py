# The logic in this file is derived from the original from Phil Bresnehan, UNCW

from argparse import ArgumentParser
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn import linear_model
from smartfin import decoder


def computeTemperatureCoeffs(reference_temps: List[float], smartfin_temps: List[float]) -> Tuple[float, float]:
    reg = linear_model.LinearRegression()
    uncalibrated = np.array(smartfin_temps).reshape(-1, 1)
    reference = np.array(reference_temps).reshape(-1, 1)
    reg.fit(X = uncalibrated, y = reference)

    return (reg.coef_[0] + reg.intercept_)

def extractSmartfinData(sf_path: Path):
    df = pd.read_csv(sf_path.as_posix(), header=None)
    data_to_decode = df.iat[0, 0]
    

def cli_calibration():
    parser = ArgumentParser()
    parser.add_argument("smartfin_data")
    parser.add_argument("temperature_data")

    args = parser.parse_args()

    smartfin_path = Path(args.smartfin_data)
    temperature_path = Path(args.temperature_data)
    if not smartfin_path.exists():
        raise RuntimeError("Path to DUT data does not exist")
    if not temperature_path.exists():
        raise RuntimeError("Path to Reference data does not exist")

    if smartfin_path.suffix != ".csv":
        raise RuntimeError("Unknown DUT file format")
    
    if temperature_path.suffix != ".txt":
        raise RuntimeError("Unknown Reference data file format")
    
    extractSmartfinData(smartfin_path)
    extractTemperatureData(temperature_path)
    
if __name__ == "__main__":
    cli_calibration()
