from time import sleep
from numpy import number
import pandas as pd
import serial
import sys

# downloads all data off of the fin through the serial port 
# and names the files in format: [fin serial #]-[file name on fin]-session-data.sfr
# then allows you to clear the files off the fin after with a prompt

#TO USE: 
# command: python3 download.py [port the fin is connected to]
# e.x.   : python3 download.py /dev/tty.usbmodem142301

#after, use decode.py (see that file for more info)

SerialPort = str(sys.argv[1]) #fin serial port entered as a command line argument
ser = serial.Serial(port = SerialPort, baudrate=115200,timeout=None)
numberOfSessions = 0
files = []

def saveDataFromSerial():
    answer = ""
    numberOfSessions = 0
    

    dataToBeDecoded = []
    fileName = ""
    j = 0

    sleep(1.1)

    ser.write(('#CLI\r').encode()) #Access CLI through terminal

    sleep(1)

    ser.write(('R\r').encode())
    
    sleep(1)

    ser.write(('R\r').encode())


    while True:
        data = ser.readline().decode()
        if('Publish Header:' in data):
            fileName = data[16:-1]
            files.append(fileName + "-session-data.sfr")
            print("Downloading " + fileName)
            

        if('{' in data):
            dataToBeDecoded.append(data)
            #print(data, end = "")

        if('packets' in data):
            df = open(fileName + "-session-data.sfr", "w") #Save each session as a new line in sfr file
            for i in range(len(dataToBeDecoded)):
                df.write(dataToBeDecoded[i][:-1] + "\n")
            numberOfSessions = numberOfSessions + 1

            df.close()
            dataToBeDecoded = []
            ser.write(('N\r').encode())
            ser.write(('R\r').encode())
            sleep(1)
        
        
        if(data == "End of Directory\n"): 
            print("Delete files off fin? Y/N: ", end = "")
            
            answer = input()
            
            sleep(0.5)
            for i in range(numberOfSessions):
                if(answer == "Y"):
                    ser.write(('D\r').encode())
                ser.write(('N\r').encode())
            sleep(0.5)
            ser.write(('D\r').encode())
            sleep(0.5)
            #print(data)
            break    
    return files

if __name__ == "__main__":
    print("Saving Data From Serial...")
    saveDataFromSerial()
    print("Files saved to paths:")
    filesheet = open("file-names.txt","w")
    for i in range(len(files)):
        print(files[i])