from doctest import DocFileTest
import serial
import sys
from decoder import *
from datetime import date
import pandas as pd
from matplotlib import pyplot as plt
from geopy.geocoders import Nominatim
from PIL import Image
today = date.today().strftime("%m|%d|%y")
#SerialPort = str(sys.argv[1]) #Enter your fin serial port name as a command line argument
geolocator = Nominatim(user_agent="smartfin")




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
        mean = dfFull["timestamp"].mean()
        
        dfFull['lostPackets'] = brokenLines
        dfFull['totalPackets'] = totalLines
        # for every row, delete it if the timestamp is > 2x the mean (plus some buffer).
        aSize = dfFull['timestamp'].size
        dfFull = dfFull[dfFull['timestamp'] < (2*mean + 10)] 
        bSize = dfFull['timestamp'].size
        lostTimeStamps = aSize - bSize
        dfFull['lostTimestamps'] = lostTimeStamps
        dfFull['timestampsBeforeLoss'] = aSize
    
        
        dfFull['DTemp'] = dfFull['Temperature'].diff(periods=300)
        #if the temperature hasnt changed much the last 6 mins
        dfFull['isSettled'] = dfFull['DTemp'].abs() < 0.2
        
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
        df.to_csv("session_data.csv")
        fig, axs = plt.subplots(3,4,figsize=(20,20))
        axs[0][0].plot(df['timestamp'], df['X Acceleration'])
        axs[0][0].set_title("Lat, Long: " + str(df['Latitude'].mean()) + ", " + str(df['Longitude'].mean()) + "\nProccessed on " + today + "\nSea Temperature: " + str(round(df['settledTemps'].median(),2)) + " degrees C\n" + str(int(df['lostPackets'].median())) + " of " +  str(int(df['totalPackets'].median())) + " total packets corrupted and proccessed out initially (" + str(round((df['lostPackets'].median()/df['totalPackets'].median())*100,2))+ "%)" + "\n" + str(int(df['lostTimestamps'].median())) + " of " + str(int(df['timestampsBeforeLoss'].median())) + " timestamps corrupted and proccessed out later (" + str(round((df['lostTimestamps'].median()/df['timestampsBeforeLoss'].median())*100,2))+ "%)\nTotal data loss of " + str(round(((df['lostPackets'].median()+(df['lostTimestamps'].median()/10))/df['totalPackets'].median())*100,2))+  "%\n(Note that 1 packet contains 10 timestamps of data)\n\nX acc vs timestamp") 
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
        #axs[0][3].set_ylim(10,40) 

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
        axs[1][3].plot(df['timestamp'], df['DTemp'])
        axs[1][3].set_title("Change in temperature 5min ago vs. timestamp: ")
        axs[1][3].axhline(0, color="orange", linestyle="dotted")

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

        plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)

        plt.savefig("session_data" + str(plotCount) + ".png")
        plt.close()
        plotCount+=1
        
decodedData = decodeFromFile(today + "-data.sfr") #INSERT FILE NAME TO BE DECODED HERE, only the date should be different
oceanTemp = 0
plotData(decodedData)

print("\n\n\n\n Success! Plotted at 'session_data0.png'")

# open method used to open different extension image file
im = Image.open("session_data0.png")  
# This method will show image in any image viewer 
im.show() 
