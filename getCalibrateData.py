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

#this code is used to collect the actual data for calibration. Use calibrateTemp to 
#get the correct calibration values based off this data
#RUN WHILE PLUGGED INTO BOTH FIN AND SBE COMMAND
#>python3 getCalibrateData.py /dev/tty.usbserial* /dev/tty.usbmodem*
#                               SBE port        fin port

    #Enter your fin serial port name as a command line argument
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