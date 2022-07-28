from doctest import DocFileTest
import os
from time import sleep
from traceback import print_last
from tracemalloc import start
from turtle import clear
from pytz import utc
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
import scipy.integrate as integrate
import scipy.special as special
from scipy.fft import fft, fftfreq, fftshift
from scipy import signal

warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=TypeError)

#This code is used to plot data given an SFR file of raw data
#RUN WITH
#>python3 robPlot.py

today = date.today().strftime("%m|%d|%y")
#SerialPort = str(sys.argv[1]) #Enter your fin serial port name as a command line argument
geolocator = Nominatim(user_agent="smartfin")
startTime = pd.Timestamp.utcnow()
oceanTemp = 0
#CHANGING SETTINGS
#240 is based on:
#https://docs.google.com/document/d/1HU__vjj-X4UscdWC5Q2WnbwtDiQQfpvlOIGNSovF1gc/edit
TIME_NEEDED_TO_SETTLE = 240 #in seconds
DEGREE_CHANGE_C_CONSIDERED_SETTLED = 0.1 #in degrees C


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
            

        fig, axs = plt.subplots(6,4,figsize=(25,28))

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

        axs[0][3].set_title("temperature vs timestamp\nMedian: " + str(round(df['Temperature'].median(),2)) + " degrees C")


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
        axs[1][3].axhline(DEGREE_CHANGE_C_CONSIDERED_SETTLED, color="orange", linestyle="dotted")
        axs[1][3].axhline(-DEGREE_CHANGE_C_CONSIDERED_SETTLED, color="orange", linestyle="dotted")
        axs[1][3].set_ylim(-1,1)

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


        #axs[3][0].scatter( df['timestamp'], (df['Water Detect'] > 0))
        #axs[3][0].set_title("Water Detect vs Time (s)")
        #FFT
        yf = fft(df['X Acceleration'].values)
        yf = fftshift(yf)
        #    1 / sampling rate
        xf = fftfreq(yf.size, 1.0)
        xf = fftshift(xf)
        axs[3][0].plot(xf, (1.0/yf.size)*abs(yf))
        axs[3][0].set_title("X acc FFT")
        axs[3][0].grid()

        #how to filter something
        #sos = signal.butter(10, 15, 'hp', fs=100, output='sos')
        #filtered = signal.sosfilt(sos, df['X Acceleration'])
        #print(filtered)

        axs[3][1].plot(df['timestamp'], df['X Acceleration'])
        axs[3][1].set_title("X acceleration")

        velox = integrate.cumulative_trapezoid(df['X Acceleration'], df['timestamp'], initial=0)
        posx = integrate.cumulative_trapezoid(velox, df['timestamp'], initial=0)

        axs[3][2].plot(df['timestamp'], velox)
        axs[3][2].set_title("X velocity")
        axs[3][2].grid()

        axs[3][3].plot(df['timestamp'], posx)
        axs[3][3].set_title("X Pos")
        axs[3][3].grid()


        yf = fft(df['Y Acceleration'].values)
        yf = fftshift(yf)
        #                 1 / sampling rate
        xf = fftfreq(yf.size, 1.0)
        xf = fftshift(xf)
        axs[4][0].plot(xf, (1.0/yf.size)*abs(yf))
        axs[4][0].set_title("Y acc FFT")
        axs[4][0].grid()






        axs[4][1].plot(df['timestamp'], df['Y Acceleration'])
        axs[4][1].set_title("Y acceleration")

        veloy = integrate.cumulative_trapezoid(df['Y Acceleration'], df['timestamp'], initial=0)
        posy = integrate.cumulative_trapezoid(veloy, df['timestamp'], initial=0)

        axs[4][2].plot(df['timestamp'], veloy)
        axs[4][2].set_title("Y velocity")
        axs[4][2].grid()

        axs[4][3].plot(df['timestamp'], posy)
        axs[4][3].set_title("Y Pos")
        axs[4][3].grid()


        yf = fft(df['Z Acceleration'].values)
        yf = fftshift(yf)
        #    1 / sampling rate
        xf = fftfreq(yf.size, 1.0)
        xf = fftshift(xf)
        axs[5][0].plot(xf, (1.0/yf.size)*abs(yf))
        axs[5][0].set_title("Z acc FFT")
        axs[5][0].grid()

        axs[5][1].plot(df['timestamp'], df['Z Acceleration'])
        axs[5][1].set_title("Z acceleration")

        veloz = integrate.cumulative_trapezoid(df['Z Acceleration'], df['timestamp'], initial=0)
        posz = integrate.cumulative_trapezoid(veloz, df['timestamp'], initial=0)

        axs[5][2].plot(df['timestamp'], veloz)
        axs[5][2].set_title("Z velocity")
        axs[5][2].grid()

        axs[5][3].plot(df['timestamp'], posz)
        axs[5][3].set_title("Z Pos")
        axs[5][3].grid()


        

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

    df = getData('credentials.json')    
    
    print(df)

    test = input()

    dfSFR = open(today + "session-data.sfr", "w") #Save each session as a new line in sfr file

    for i in range(len(df['published_at'])):
        if(df['published_at'][i] > startTime):
            dfSFR.write(df['data'][i] + "\n")
    
    dfSFR.close()

def openAndShowImage():
    # open method used to open different extension image file
    im = Image.open("session_data.png")  
    # This method will show image in any image viewer 
    im.show()

#Actual proccess to run:
os.system('clear')

print("""Name graph: """, end="")

#Get name from user
nameOfSession = ""
nameOfSession = input()
print("Use serialPort.py to download files.")
print("Input relative file path (file name) to plot: ", end="")
ans = ""
ans = input()

if(ans == "C"):
    #pull data from sheet and populate sfr file
    saveDataFromSheet()

if(ans == ""):
    decodedData = decodeFromFile(today + "session-data.sfr") #INSERT FILE NAME TO BE DECODED HERE, only the date should be different
else:
    decodedData = decodeFromFile(ans) #INSERT FILE NAME TO BE DECODED HERE, only the date should be different

plotData(decodedData)
#os.system('clear')
print("\nSuccess! Plotted in session_data.png\nOpening now...")
openAndShowImage()

