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

    sleep(2)
    #this block makes sure its where we want it (to not be in CLI mode)
    #so that when we go into CLI mode its at the start of it
    for i in range(10):
        ser.write(('N\r').encode())
    ser.write(('D\r').encode())

    sleep(0.1)

    ser.write(('#CLI\r').encode()) #Access CLI through terminal

    sleep(0.5)

    ser.write(('R\r').encode())
            
    ser.write(('R\r').encode())

    while True:
        data = ser.readline().decode()

        print(data + "\n")

        if('Publish Header:' in data):
            fileName = data[16:-1]

        if('{' in data):
            dataToBeDecoded.append(data)

        if('packets' in data):
            df = open(fileName + "-session-data.sfr", "w") #Save each session as a new line in sfr file
            for i in range(len(dataToBeDecoded)):
                df.write(dataToBeDecoded[i][:-1] + "\n")

            df.close()
            ser.write(('N\r').encode())
            ser.write(('R\r').encode())
        
        
        if(data == "End of Directory\n"): #Continue reading and appending decoded files to array until end of directory
            ser.write(('D\r').encode()) #exits CLI
            print("End of data.")
            break

print("Saving Data From Serial...")
saveDataFromSerial()


