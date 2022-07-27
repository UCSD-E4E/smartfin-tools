from time import sleep
from numpy import number
import pandas as pd
import serial
import sys

#TO USE: 
# command: python3 download.py [port the fin is connected to]
# e.g.   : python3 download.py /dev/tty.usbmodem142301
# WHAT IT DOES:
# downloads all data off of the fin through the serial port 
# and names the files in format: [serial #]-[file name on fin]-session-data.sfr
# then allows you to clear the files off the fin after

SerialPort = str(sys.argv[1]) #Enter your fin serial port name as a command line argument
ser = serial.Serial(port = SerialPort, baudrate=115200,timeout=None)
numberOfSessions = 0

def saveDataFromSerial():
    numberOfSessions = 0
    

    dataToBeDecoded = []
    fileName = ""
    j = 0

    sleep(1)

    print("OPENING CLI")
    ser.write(('#CLI\r').encode()) #Access CLI through terminal

    sleep(1)

    ser.write(('R\r').encode())
    
    sleep(1)

    ser.write(('R\r').encode())


    while True:
        data = ser.readline().decode()
        if('Publish Header:' in data):
            fileName = data[16:-1]
            print("FILENAME: " + fileName)
            

        if('{' in data):
            dataToBeDecoded.append(data)
            print(data, end = "")

        if('packets' in data):
            df = open("_" + fileName + "-session-data.sfr", "w") #Save each session as a new line in sfr file
            for i in range(len(dataToBeDecoded)):
                df.write(dataToBeDecoded[i][:-1] + "\n")
            numberOfSessions = numberOfSessions + 1

            df.close()
            dataToBeDecoded = []
            ser.write(('N\r').encode())
            ser.write(('R\r').encode())
            print("...")
            sleep(1)
        
        
        if(data == "End of Directory\n"): 
            print("Delete all files? Y/N")
            answer = input()     
            

            
            sleep(1)
            for i in range(numberOfSessions):
                if(answer == "Y"):
                    ser.write(('D\r').encode())
                ser.write(('N\r').encode())
            sleep(1)
            ser.write(('D\r').encode())
            sleep(1)
            print(data)
            break

            

print("Saving Data From Serial...")
saveDataFromSerial()
print("Data downloaded.")