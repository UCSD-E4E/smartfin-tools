'''Temperature Calibrator

This code is used to collect temperature data from both the fin and the SBE-37
with synced timestamps in order to calibrate the fin to the accuracy of the SBE-37.
returns a file in the directory called "SBETemperatures_[TIME].csv"
use download.py + decode.py to get the temperatures off the fin later.

To emphasize this, the timestamps you get from the fin and SBETemperatures[...].csv
will be synced up to be able to compare temperature readings.


SETUP: PLUG IN BOTH FIN AND SBE-37 INTO COMPUTER BEFORE RUNNING COMMAND
MAKE SURE THE FIN IS RESET AND ENTERS CHARGE MODE

RUN COMMAND FORMAT:
python3 getCalibrateData.py [SBE-27SI PORT ON DEVICE] [FIN USB PORT ON DEVICE]
EXAMPLE:
python3 getCalibrateData.py  /dev/tty.usbserial14421        /dev/tty.usbmodem23314
                              SBE port on computer          fin port on computer

note: make sure the firmware on your fin allows you to force a session using the 'S'
command in the CLI interface by getting into the fin's CLI and typing '#'.
If you cannot see 'S to force session' try the 'force_session' branch on github and install
that firmware for the calibration.
'''
import argparse
import datetime as dt
from time import sleep

import pandas as pd
import serial


def calibrate_temp(
        fin_port: str,
        seabird_port: str,
        iterations: int):
    """Executes the calibration sequence

    Args:
        fin_port (str): Fin port
        seabird_port (str): Seabird CTD port
        iterations (int): Number of iterations
    """
    # pylint: disable=too-many-locals
    fin_serial = serial.Serial(port=fin_port, baudrate=115200)
    seabird_serial = serial.Serial(port=seabird_port, baudrate=9600)

    start_time = dt.datetime.now()

    sleep(2)

    fin_serial.write(('#CLI\r').encode()) #Access CLI through terminal
    sleep(1)
    fin_serial.write(('S\r').encode()) #Access CLI through terminal
    sleep(1)
    fin_serial.write(((str)(iterations*2) + '\r').encode()) #Access CLI through terminal
    starttime = dt.datetime.now()
    fulltime = str(round((iterations*2.138)/60, 1))
    print("Starting time is: " + (str)(starttime))
    print("Estimated time is " + fulltime + " minutes")
    temperatures = []
    datetimes = []
    for i in range(iterations):
        seabird_serial.write(('ts\r').encode())
        sleep(0.5)
        line = ""
        while True:
            line = seabird_serial.readline().decode()
            read_time = dt.datetime.now()
            if "." in line:
                print(line[2:9], end = ",")
                print(read_time, end = ", ")
                print("percent complete: " + str(i*100/iterations) + "%")
                line = line[2:9]
                temperatures.append((float)(line))
                datetimes.append(read_time)
                break

    timestamps = [(timestamp - start_time).total_seconds() for timestamp in datetimes]

    data = {
        'datetimes': datetimes,
        'timestamps': timestamps,
        'true temps': temperatures
    }

    dataframe = pd.DataFrame(data)

    dataframe.to_csv("SBETemperatures_" + (str)(start_time) + ".csv")
    print(dataframe)

def main():
    """Bootstraps CLI for calibration
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('fin_port', type=str)
    parser.add_argument('seabird_port', type=str)
    parser.add_argument('iterations', type=int)
    args = parser.parse_args()
    calibrate_temp(
        fin_port=args.fin_port,
        seabird_port=args.seabird_port,
        iterations=args.iterations
    )

if __name__ == '__main__':
    main()
