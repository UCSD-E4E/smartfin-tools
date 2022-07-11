from doctest import DocFileTest
import os
from time import sleep
from traceback import print_last
from tracemalloc import start
from turtle import clear
from pytz import utc
import serial
import sys
from decoder import *
from dataEndpoint import *
from datetime import date
from datetime import datetime as dt
import datetime
import pandas as pd
from matplotlib import pyplot as plt
from geopy.geocoders import Nominatim
from PIL import Image
import warnings
import requests
import dataEndpoint
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=TypeError)

today = date.today().strftime("%m|%d|%y")
SerialPort = str(sys.argv[1]) #Enter your fin serial port name as a command line argument
geolocator = Nominatim(user_agent="smartfin")
startTime = pd.Timestamp.utcnow()
oceanTemp = 0
#CHANGING SETTINGS
#240 is based on:
#https://docs.google.com/document/d/1HU__vjj-X4UscdWC5Q2WnbwtDiQQfpvlOIGNSovF1gc/edit
TIME_NEEDED_TO_SETTLE = 240 #in seconds
DEGREE_CHANGE_C_CONSIDERED_SETTLED = 0.2 #in degrees C


# For example, $ python3 DataGetter.py /dev/ttyACM0

def decodeFromFile(filepath:str): #Decode data from given file and return as an array with n pandas dataframes (n = number of sessions in file)
    
    pdArray = []
    brokenLines = 0
    totalLines = 0
    with open(filepath) as df:
        for line in df:
            totalLines = totalLines + 1
            try:
                currentRecord = decodeRecord(line.strip())
                df = pd.DataFrame (currentRecord, columns = ['timestamp','temp+water', 'xAcc','yAcc', 'zAcc', 'xGyro', 'yGyro', 'zGyro', 'xMag','yMag','zMag','lat','lon'])
                df = convertToSI(df)
                if(len(pdArray) > 0):
                    pdArray[0] = pdArray[0].append(df)
                else:
                    pdArray.append(df)
            except:
                brokenLines = brokenLines + 1
    try:
        dfFull = pdArray[0].sort_values(by=['timestamp'])
        medianTimeStamp = dfFull["timestamp"].median()
        
        dfFull['lostPackets'] = brokenLines
        dfFull['totalPackets'] = totalLines
        # for every row, delete it if the timestamp is > 2x the median (plus some buffer).
        aSize = dfFull['timestamp'].size
        dfFull = dfFull[dfFull['timestamp'] < (2*medianTimeStamp + 50)] 
        bSize = dfFull['timestamp'].size
        lostTimeStamps = aSize - bSize
        dfFull['lostTimestamps'] = lostTimeStamps
        dfFull['timestampsBeforeLoss'] = aSize

        #THIS BLOCK GETS RID OF ALL THE WEIRD DEFAULT VALUES
        #DONOTE 0.205 IS THE CURRENT CALIBRATION NUMBER
        dfFull['TemperatureMessed'] = dfFull['Temperature'] != 0.205
        temporary = (dfFull['TemperatureMessed']) * (dfFull['Temperature'])
        dfFull['Temperature'] = temporary
        dfFull['Temperature'] = dfFull['Temperature'].replace({'0':np.nan, 0:np.nan})

        
        dfFull['DTemp'] = dfFull['Temperature'].diff(periods=TIME_NEEDED_TO_SETTLE)
        dfFull['DTempFuture'] = dfFull['Temperature'].diff(periods=-TIME_NEEDED_TO_SETTLE)
        #if the temperature hasnt changed much the last 6 mins
        dfFull['isSettled'] = (dfFull['DTemp'].abs() < DEGREE_CHANGE_C_CONSIDERED_SETTLED) & (dfFull['DTempFuture'].abs() < DEGREE_CHANGE_C_CONSIDERED_SETTLED)
        
        temporary = (dfFull['isSettled']) * dfFull['Temperature']
        dfFull['settledTemps'] = temporary
        dfFull['settledTemps'] = dfFull['settledTemps'].replace({'0':np.nan, 0:np.nan})

        pdArray[0] = dfFull

    except:
        print('AN ERROR OCCURED WITH DECODING')
    return pdArray

def plotData(files):

    plotCount = 0
    for df in files:
        #gets location name
        location = "Location not available."
        try:
            if(df['Latitude'][0].any()):
                geoKey = "a6c6d800c1addf8a47634c8d5b917686"
                geoLink = "http://api.positionstack.com/v1/reverse?access_key=" + geoKey + "&query=" + str(df['Latitude'].mean()) + "," + str(df['Longitude'].mean())
                response = requests.get(geoLink)
                location = str(response.json()['data'][0]['label'])
                print("\n"+location+"\n")
        except:
            print("Locate not available.")
            

        fig, axs = plt.subplots(3,4,figsize=(25,28))

        axs[0][0].plot(df['timestamp'], df['X Acceleration'])
        axs[0][0].set_title(str(nameOfSession) + "\nLocation: " + (location if location else "unknown") + "\n(" + str(df['Latitude'].mean()) + ", " + str(df['Longitude'].mean()) + ")\n" + "\nProccessed on " + today + "\nSea Temperature: " + str(round(df['settledTemps'].median(),2)) + " degrees C\n" + str((df['lostPackets'].median())) + " of " +  str((df['totalPackets'].median())) + " total packets corrupted and proccessed out initially (" + str(round((df['lostPackets'].median()/df['totalPackets'].median())*100,2))+ "%)" + "\n" + str((df['lostTimestamps'].median())) + " of " + str((df['timestampsBeforeLoss'].median())) + " timestamps corrupted and proccessed out later (" + str(round((df['lostTimestamps'].median()/df['timestampsBeforeLoss'].median())*100,2))+ "%)\nTotal data loss of " + str(round(((df['lostPackets'].median()+(df['lostTimestamps'].median()/10))/df['totalPackets'].median())*100,2))+  "% (1 packet = 10 timestamps of data)\n\nX acc vs timestamp") 
        axs[0][0].set_ylim(-3,3)
        axs[0][0].axhline(0, color="orange", linestyle="dotted")
        axs[0][0].axhline(1, color="orange", linestyle="dotted", label = '1g')
        axs[0][1].plot(df['timestamp'], df['Y Acceleration'])
        axs[0][1].set_ylim(-3,3)
        axs[0][1].set_title("Y acc vs timestamp")
        axs[0][1].axhline(0, color="orange", linestyle="dotted")
        axs[0][1].axhline(1, color="orange", linestyle="dotted")
        axs[0][2].plot(df['timestamp'], df['Z Acceleration'])
        axs[0][2].set_ylim(-3,3)
        axs[0][2].set_title("Z acc vs timestamp")
        axs[0][2].axhline(0, color="orange", linestyle="dotted")
        axs[0][2].axhline(1, color="orange", linestyle="dotted")
        axs[0][3].plot(df['timestamp'], df['Temperature'])
        axs[0][3].plot(df['timestamp'], df['settledTemps'], color = "orange")
        axs[0][3].axhline(df['settledTemps'].median(), color="orange", linestyle="dotted")
        #sets to limits of realistic ocean temps
        #axs[0][3].set_ylim(15,25) 

        axs[0][3].set_title("temperature vs timestamp\nMedian: " + str(round(df['Temperature'].mean(),2)) + " degrees C")


        axs[1][0].plot(df['timestamp'], df['X Angular Velocity'])
        axs[1][0].set_title("X gyro vs timestamp")
        axs[1][0].set_ylim(-300,300) 
        axs[1][0].axhline(0, color="orange", linestyle="dotted")
        axs[1][1].plot(df['timestamp'], df['Y Angular Velocity'])
        axs[1][1].set_ylim(-300,300)
        axs[1][1].axhline(0, color="orange", linestyle="dotted")
        axs[1][1].set_title("Y gyro vs timestamp")
        axs[1][2].plot(df['timestamp'], df['Z Angular Velocity'])
        axs[1][2].set_ylim(-300,300)
        axs[1][2].set_title("Z gyro vs timestamp")
        axs[1][2].axhline(0, color="orange", linestyle="dotted")
        axs[1][3].plot(df['timestamp'], df['Temperature'].diff(periods=1))
        axs[1][3].plot(df['timestamp'], df['DTemp'])
        axs[1][3].plot(df['timestamp'], df['DTempFuture'])
        axs[1][3].set_title("Δ temperature over\nBlue: 1s, Orange: 5min, Green: -5min")
        axs[1][3].axhline(0, color="orange", linestyle="dotted")
        axs[1][3].axhline(0.2, color="orange", linestyle="dotted")
        axs[1][3].axhline(-0.2, color="orange", linestyle="dotted")

        axs[2][0].scatter( df['timestamp'], df['X Magnetic Field'])
        axs[2][0].set_ylim(-6000,6000)
        axs[2][0].set_title("X mag vs timestamp")
        axs[2][1].scatter(df['timestamp'], df['Y Magnetic Field'])
        axs[2][1].set_ylim(-6000,6000)
        axs[2][1].set_title("Y mag vs timestamp")
        axs[2][2].scatter(df['timestamp'], df['Z Magnetic Field'])
        axs[2][2].set_ylim(-6000,6000)
        axs[2][2].set_title("Z mag vs timestamp")
        axs[2][3].scatter(df['timestamp'], df['settledTemps'])
        axs[2][3].set_title("Temps. When Settled / Est. Sea Temp.\nMean: " + str(round(df['settledTemps'].mean(),2)) + " degrees C\nMedian: " + str(round(df['settledTemps'].median(),2)) + " degrees C")
        axs[2][3].axhline(df['settledTemps'].median(), color="orange", linestyle="dotted")
        #axs[2][3].set_xlim(df['timestamp'].min(), df['timestamp'].max())
        #axs[2][3].set_ylim(df['Temperature'].min(), df['Temperature'].max())


        #follwing code is to be able to graph cardinal direction eventually. 
        #make sure to change '.subplots(3,4,fi' to '.subplots(4,4,fi'
        #if you want to use the following code. 
        #xovery = df['X Magnetic Field']/df['Y Magnetic Field']
        #yoverx = df['Y Magnetic Field']/df['X Magnetic Field']
        #df['atan(X/Y)'] = np.rad2deg(np.arctan(xovery))*4
        #df['atan(Y/X)'] = np.rad2deg(np.arctan(yoverx))*4
        #axs[3][0].scatter( df['timestamp'], df['atan(X/Y)'])
        #axs[3][0].set_title("atan(x/y) vs time")
        #axs[3][0].set_ylim(-10,370)
        #axs[3][1].scatter( df['timestamp'], df['atan(Y/X)'])
        #axs[3][1].set_title("atan(y/x) vs time")
        #axs[3][1].set_ylim(-10,370)
        #axs[3][1].axhline(0, color="orange", linestyle="dotted")
        #axs[3][1].axhline(90, color="orange", linestyle="dotted")
        #axs[3][1].axhline(180, color="orange", linestyle="dotted")
        #axs[3][1].axhline(270, color="orange", linestyle="dotted")
        #axs[3][1].axhline(360, color="orange", linestyle="dotted")

        

        plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)

        plt.savefig("session_data.png")
        df.to_csv("session_data_"+ str(startTime) + ".csv")
        plt.close()
        plotCount+=1

def saveDataFromSheet():
    #dfSheet = dataEndpoint

    dfSFR = open("_" + str(startTime) + "-data.sfr", "w") #Save each session as a new line in sfr file
    df = pd.read_json('jsonofhook.json')

    for i in range(len(df['published_at'])):
        if(df['published_at'][i] > startTime):
            dfSFR.write(df['data'][i] + "\n")
    dfSFR.close()

def saveDataFromSerial():
    ser = serial.Serial(port = SerialPort, baudrate=115200,timeout=None)

    dataToBeDecoded = []

    #this block makes sure its where we want it (to not be in CLI mode)
    #so that when we go into CLI mode its at the start of it
    ser.write(('N\r').encode())
    ser.write(('N\r').encode())
    ser.write(('N\r').encode())
    ser.write(('N\r').encode())
    ser.write(('N\r').encode())
    ser.write(('D\r').encode())

    ser.write(('#CLI\r').encode()) #Access CLI through terminal

    sleep(1)


    ser.write(('R\r').encode())
            
    ser.write(('R\r').encode())

    while True:
        data = ser.readline().decode()
        #print(data)
        if('{' in data):
            dataToBeDecoded.append(data)

        #ser.write(('D\r').encode()) #deletes data
        ser.write(('N\r').encode())
        
        
        if(data == "End of Directory\n"): #Continue reading and appending decoded files to array until end of directory
            ser.write(('D\r').encode()) #exits CLI
            break
        
        ser.write(('R\r').encode())

    df = open("_" + str(startTime) + "-data.sfr", "w") #Save each session as a new line in sfr file

    for i in range(len(dataToBeDecoded)):
        df.write(dataToBeDecoded[i][:-1] + "\n")

    df.close()

def openAndShowImage():
    # open method used to open different extension image file
    im = Image.open("session_data.png")  
    # This method will show image in any image viewer 
    im.show()
    return 0

#Actual proccess to run:
os.system('clear')
print("""
   _____                          _    ______  _        
  / ____|                        | |  |  ____|(_)       
 | (___   _ __ ___    __ _  _ __ | |_ | |__    _  _ __  
  \___ \ | '_ ` _ \  / _` || '__|| __||  __|  | || '_ \ 
  ____) || | | | | || (_| || |   | |_ | |     | || | | |
 |_____/ |_| |_| |_| \__,_||_|    \__||_|     |_||_| |_|
                    -.--.
                   )  " '-,
                   ',' 2  \_
                    \q \ .  |
                 _.--'  '----.__
                /  ._      _.__ \__
             _.'_.'  \_ .-._\_ '-, }
            (,/ _.---;-(  . \ \   ~
          ____ (  .___\_\  \/_/
         (      '-._ \   \ |
          '._       ),> _) >
             '-._  c=        -._
                 '-._           '.
                     '-._         `_
                         '-._       '.
                             '-._     |
                                 `~---'
            
                     Begin session now!
                  """+str(startTime)+"""
Name session and press enter once session is complete and uploaded...

Name:""", end="")
#Get name from user
nameOfSession = ""
nameOfSession = input()
print("Data from online cloud (C), Serial (S), or file (F, default): ", end="")
ans = ""
ans = input()

if(ans == "C"):
    #pull data from sheet and populate sfr file
    saveDataFromSheet()
if(ans == "S"):
    saveDataFromSerial()

#decode and plot the data
decodedData = decodeFromFile("_" + str(startTime) + "-data.sfr") #INSERT FILE NAME TO BE DECODED HERE, only the date should be different
plotData(decodedData)
#os.system('clear')
print("\nSuccess! Plotted in session_data.png\nOpening now...")
openAndShowImage()

