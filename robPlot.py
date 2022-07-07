from doctest import DocFileTest
import serial
import sys
from decoder import *
from datetime import date
import pandas as pd
from matplotlib import pyplot as plt
from geopy.geocoders import Nominatim
today = date.today().strftime("%m|%d|%y")
#SerialPort = str(sys.argv[1]) #Enter your fin serial port name as a command line argument
geolocator = Nominatim(user_agent="smartfin")


# For example, $ python3 DataGetter.py /dev/ttyACM0

def decodeFromFile(filepath:str): #Decode data from given file and return as an array with n pandas dataframes (n = number of sessions in file)
    pdArray = []
    with open(filepath) as df:
        for line in df:
            currentRecord = decodeRecord(line.strip())
            df = pd.DataFrame (currentRecord, columns = ['timestamp','temp+water', 'xAcc','yAcc', 'zAcc', 'xGyro', 'yGyro', 'zGyro', 'xMag','yMag','zMag','lat','lon'])
            df = convertToSI(df)
            if(len(pdArray) > 0):
                pdArray[0] = pdArray[0].append(df)
            else:
                pdArray.append(df)
    
    return pdArray

def plotData(files):
    plotCount = 0
    for df in files:
        df.to_csv("session_data.csv")
        fig, axs = plt.subplots(3,4,figsize=(20,20))
        axs[0][0].plot(df['timestamp'], df['X Acceleration'])
        axs[0][0].set_title("X acc vs timestamp")
        axs[0][0].set_ylim(-3,3)
        axs[0][1].plot(df['timestamp'], df['Y Acceleration'])
        axs[0][1].set_ylim(-3,3)
        axs[0][1].set_title("Y acc vs timestamp")
        axs[0][2].plot(df['timestamp'], df['Z Acceleration'])
        axs[0][2].set_ylim(-3,3)
        axs[0][2].set_title("Z acc vs timestamp")
        axs[0][3].plot(df['timestamp'], df['Temperature'])
        axs[0][3].set_ylim(10,40)
        axs[0][3].set_title("temperature vs timestamp")


        axs[1][0].plot(df['timestamp'], df['X Angular Velocity'])
        axs[1][0].set_title("X gyro vs timestamp")
        axs[1][0].set_ylim(-600,600) 
        axs[1][1].plot(df['timestamp'], df['Y Angular Velocity'])
        axs[1][1].set_ylim(-600,600)
        axs[1][1].set_title("Y gyro vs timestamp")
        axs[1][2].plot(df['timestamp'], df['Z Angular Velocity'])
        axs[1][2].set_ylim(-600,600)
        axs[1][2].set_title("Z gyro vs timestamp")
        axs[1][3].plot(df['timestamp'], df['Latitude'])
        axs[1][3].set_ylim(32,33)
        axs[1][3].set_title("Latitude: " + str(df['Latitude'].mean()))

        axs[2][0].plot(df['timestamp'], df['X Magnetic Field'])
        axs[2][0].set_ylim(-6000,6000)
        axs[2][0].set_title("X mag vs timestamp")
        axs[2][1].plot(df['timestamp'], df['Y Magnetic Field'])
        axs[2][1].set_ylim(-6000,6000)
        axs[2][1].set_title("Y mag vs timestamp")
        axs[2][2].plot(df['timestamp'], df['Z Magnetic Field'])
        axs[2][2].set_ylim(-6000,6000)
        axs[2][2].set_title("Z mag vs timestamp")
        axs[2][3].plot(df['timestamp'], df['Longitude'])
        axs[2][3].set_ylim(-117,-118)
        axs[2][3].set_title("Longitude: " + str(df['Longitude'].mean()))

        plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)

        plt.savefig("session_data" + str(plotCount) + ".png")
        plt.close()
        plotCount+=1
        
decodedData = decodeFromFile("07|06|22-data.sfr") #INSERT FILE NAME TO BE DECODED HERE, only the date should be different
plotData(decodedData)

