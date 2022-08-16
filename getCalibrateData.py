#imports
import pandas as pd
import warnings
import matplotlib.pyplot as plt
import numpy as np
from requests import session
import serial
import sys
from time import sleep, time
import datetime
import os

#This code is used to collect temperature data from both the fin and the SBE-37
#with synced timestamps in order to calibrate the fin to the accuracy of the SBE-37.
#returns a file in the directory called "SBETemperatures_[TIME].csv"
#use download.py + decode.py to get the temperatures off the fin later.

#To emphasize this, the timestamps you get from the fin and SBETemperatures[...].csv
#will be synced up to be able to compare temperature readings.


#SETUP: PLUG IN BOTH FIN AND SBE-37 INTO COMPUTER BEFORE RUNNING COMMAND
#MAKE SURE THE FIN IS RESET AND ENTERS CHARGE MODE

#RUN COMMAND FORMAT: 
#python3 getCalibrateData.py [SBE-27SI PORT ON DEVICE] [FIN USB PORT ON DEVICE]
#EXAMPLE: 
#python3 getCalibrateData.py  /dev/tty.usbserial14421        /dev/tty.usbmodem23314
#                               SBE port on computer          fin port on computer

#note: make sure the firmware on your fin allows you to force a session using the 'S'
#command in the CLI interface by getting into the fin's CLI and typing '#'.
#If you cannot see 'S to force session' try the 'force_session' branch on github and install
#that firmware for the calibration. 

    #Fin
SerialPortFin = str(sys.argv[2]) 
serFin = serial.Serial(port = SerialPortFin, baudrate=115200,timeout=None)

    #SBE
SerialPortSBE = str(sys.argv[1]) #sbe port
serSBE = serial.Serial(port = SerialPortSBE, baudrate=9600,timeout=None)

session_time = 0
df = pd.DataFrame
startTime = datetime.datetime.now()

def runCalibrationCollect():
    print("Enter sample # of calibration session collection: ", end = "")
    session_time = (int)(input())
    print("##########################################################")

    sleep(2)

    serFin.write(('#CLI\r').encode()) #Access CLI through terminal
    sleep(1)
    serFin.write(('S\r').encode()) #Access CLI through terminal
    sleep(1)
    serFin.write(((str)(session_time*2) + '\r').encode()) #Access CLI through terminal
    starttime = datetime.datetime.now()
    fulltime = str(round((session_time*2.138)/60, 1))
    os.system('say calibrating. Estimated time is ' + fulltime + ' minutes')
    print("Starting time is: " + (str)(starttime))
    print("Estimated time is " + fulltime + " minutes")
    temperatures = []
    datetimes = []
    for i in range(session_time):
        serSBE.write(('ts\r').encode())  
        sleep(0.5)
        line = ""
        while True:
            line = serSBE.readline().decode()
            read_time = datetime.datetime.now()
            if ("." in line):
                print(line[2:9], end = ",")
                print(read_time, end = ", ")
                print("percent complete: " + str(i*100/session_time) + "%")
                line = line[2:9]
                temperatures.append((float)(line))
                datetimes.append(read_time)
                break
    
    os.system('say calibration complete')

    timestamps = [None] * len(datetimes)
    for j in range(len(datetimes)):
        timestamps[j] = datetimes[j] - starttime
        timestamps[j] = timestamps[j].total_seconds()
        
    data = {
        'datetimes': datetimes,
        'timestamps': timestamps,
        'true temps': temperatures
    }

    df = pd.DataFrame(data)

    df.to_csv("SBETemperatures_" + (str)(startTime) + ".csv")
    print(df)



runCalibrationCollect()