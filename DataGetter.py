from doctest import DocFileTest
import serial
import sys
from decoder import *
from datetime import date
import pandas as pd
today = date.today().strftime("%m|%d|%y")
SerialPort = str(sys.argv[1]) #Enter your fin serial port name as a command line argument

def saveRawData():
    ser = serial.Serial(port = SerialPort, baudrate=115200,timeout=None)

    dataToBeDecoded = []

    ser.write(('#CLI\r').encode()) #Access CLI through terminal

    ser.write(('R\r').encode())
            
    ser.write(('R\r').encode())

    while True:
        data = ser.readline().decode()
        # print(data)
        if('{' in data):
            dataToBeDecoded.append(data)

        ser.write(('N\r').encode())
        
        if(data == "End of Directory\n"): #Continue reading and appending decoded files to array until end of directory
            break
        
        ser.write(('R\r').encode())

    df = open(today + "-data.sfr", "x") #Save each session as a new line in sfr file
    for i in range(len(dataToBeDecoded)):
        df.write(dataToBeDecoded[i][:-1] + "\n")

    df.close()


def decodeFromFile(filepath:str): #Decode data from given file and return as a pandas dataframe
    with open(filepath) as df:
        for line in df:
            return decodeRecord(line.strip())
            

saveRawData()
decodedData = decodeFromFile("FILENAME")

