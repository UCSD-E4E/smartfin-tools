from doctest import DocFileTest
import serial
import sys
from decoder import *
from datetime import date
import pandas as pd
from matplotlib import pyplot as plt
from time import sleep

CLI_WAIT = 2

today = date.today().strftime("%m_%d_%y")
SerialPort = str(sys.argv[1]) #Enter your fin serial port name as a command line argument
# For example, $ python3 DataGetter.py /dev/ttyACM0

raw_data_fp = "./{date}_raw_data.sfr"
csv_data_fp = "./{date}_session{session_num}.csv"
plot_data_fp = "./{date}_session{session_num}_plt.png"

def saveRawData(fp):
    ser = serial.Serial(port = SerialPort, baudrate=115200,timeout=None)
    dataToBeDecoded = []

    ser.write(('#CLI\r').encode()) #Access CLI through terminal

    sleep(CLI_WAIT)
    ser.write(('R\r').encode()) #Accesses file system

    while True:
        data = ser.readline().decode() #Reads console output
        if(data == "End of Directory\n"): #Continue reading and appending decoded files to array until end of directory
            break
    
        ser.write(('R\r').encode()) #Displays file contents (encoded)
        if('{' in data):
            dataToBeDecoded.append(data) #Adds data to list if valid

        ser.write(('N\r').encode()) #Next file

    ser.write(('X\r').encode()) #Exits CLI state

    #writes data to file
    with open(fp, "a") as df:
        for i in range(len(dataToBeDecoded)):
            df.write(dataToBeDecoded[i][:-1] + "\n")



def decodeFromFile(filepath:str): #Decode data from given file and return as an array with n pandas dataframes (n = number of sessions in file)
    pdArray =[]
    with open(filepath) as df:
        for line in df:
            currentRecord = decodeRecord(line.strip())
            df = pd.DataFrame (currentRecord, columns = ['timestamp','temp+water', 'xAcc','yAcc', 'zAcc', 'xGyro', 'yGyro', 'zGyro', 'xMag','yMag','zMag','lat','lon'])
            df = convertToSI(df)
            pdArray.append(df)


    return pdArray

def plotData(files):
    for i, df in enumerate(files):
        fig, axs = plt.subplots(3,4,figsize=(15,15))
        axs[0][0].plot(df['timestamp'], df['X Acceleration'])
        axs[0][0].set_title("X acc vs timestamp")
        axs[0][1].plot(df['timestamp'], df['Y Acceleration'])
        axs[0][1].set_title("Y acc vs timestamp")
        axs[0][2].plot(df['timestamp'], df['Z Acceleration'])
        axs[0][2].set_title("Z acc vs timestamp")
        axs[0][3].plot(df['timestamp'], df['Temperature'])
        axs[0][3].set_title("temperature vs timestamp")


        axs[1][0].plot(df['timestamp'], df['X Angular Velocity'])
        axs[1][0].set_title("X gyro vs timestamp")
        axs[1][1].plot(df['timestamp'], df['Y Angular Velocity'])
        axs[1][1].set_title("Y gyro vs timestamp")
        axs[1][2].plot(df['timestamp'], df['Z Angular Velocity'])
        axs[1][2].set_title("Z gyro vs timestamp")
        axs[1][3].plot(df['timestamp'], df['lat'])
        axs[1][3].set_title("latitude vs timestamp")

        axs[2][0].plot(df['timestamp'], df['X Magnetic Field'])
        axs[2][0].set_title("X mag vs timestamp")
        axs[2][1].plot(df['timestamp'], df['Y Magnetic Field'])
        axs[2][1].set_title("Y mag vs timestamp")
        axs[2][2].plot(df['timestamp'], df['Z Magnetic Field'])
        axs[2][2].set_title("Z mag vs timestamp")
        axs[2][3].plot(df['timestamp'], df['lon'])
        axs[2][3].set_title("longitutde vs timestamp")

        plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)

        plt.savefig(plot_data_fp.format(date=today, session_num=i))
        plt.close()

def save_to_csv(decodedData):
    for i, df in enumerate(decodedData):
        df.to_csv(csv_data_fp.format(date=today, session_num=i), sep=",")

if __name__ == "__main__":
    raw_data_fp_today = raw_data_fp.format(date=today)
    saveRawData(raw_data_fp_today)
    decodedData = decodeFromFile(raw_data_fp_today) #INSERT FILE NAME TO BE DECODED HERE, only the date should be different
    save_to_csv(decodedData)
    plotData(decodedData)

