from time import sleep
import pandas as pd
import serial
import sys

SerialPort = str(sys.argv[1]) #Enter your fin serial port name as a command line argument


def saveDataFromSerial():
    ser = serial.Serial(port = SerialPort, baudrate=115200,timeout=None)

    dataToBeDecoded = []
    fileName = ""
    j = 0

    sleep(1)

    print("OPENING CLI")
    ser.write(('#CLI\r').encode()) #Access CLI through terminal

    sleep(1)

    ser.write(('R\r').encode())
            
    ser.write(('R\r').encode())

    while True:
        data = ser.readline().decode()
        print(data)
        if('Publish Header:' in data):
            fileName = data[16:-1]
            print("FILENAME: " + fileName)

        if('{' in data):
            dataToBeDecoded.append(data)
            print(data, end = "")

        if('packets' in data):
            df = open(fileName + "-session-data.sfr", "w") #Save each session as a new line in sfr file
            for i in range(len(dataToBeDecoded)):
                df.write(dataToBeDecoded[i][:-1] + "\n")

            df.close()
            ser.write(('N\r').encode())
            ser.write(('R\r').encode())
            print("ENCODED N, R")
        
        
        if(data == "End of Directory\n"): #Continue reading and appending decoded files to array until end of directory
            sleep(0.5)
            print("\n")
            print("End of data. Restart with magnet")
            break

print("Saving Data From Serial...")
saveDataFromSerial()



