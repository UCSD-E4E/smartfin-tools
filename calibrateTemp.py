
#imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from requests import session
from time import sleep

#Put data for time, fin temp, and SBE temp in the CSV "calibrate.csv"
#and this script will run based on those datapoiunts and spit out a 
#calibration. 
#RUN WITH:
#>python3 calibrateTemp.py

#variables
TIME_NEEDED_TO_SETTLE = 240
DEGREE_CHANGE_C_CONSIDERED_SETTLED = 0.2
file_path = ""
number_temps = 0
tempsTrue = []
tempsFin = []
session_time = 0
df = pd.DataFrame()


#gets information on the user about how the calibration was performed
def getCalibrationDataManual():
    print("How many temperatures?: ", end="")
    number_temps = (int)(input())

    tempsTrue = [0] * number_temps
    tempsFin = [0] * number_temps

    print("")

    for i in range(number_temps):
        print("Input ground truth celcius temperature " + (str)(i+1) + ": ", end="")
        tempsTrue[i] = (float)(input())
        print("Input avg. fin celcius temperature " + (str)(i+1) + ": ", end="")
        tempsFin[i] = (float)(input())

        print(" Truth: " + str(tempsTrue[i]))
        print(" Fin: " + str(tempsFin[i]))
        print("")

    data = {
        "fin temp": tempsFin,
        "true temp": tempsTrue
    }
    return pd.DataFrame(data)

#get it from the csv file "calibrate.csv"
def getCalibrateDataCSV():
    df = pd.read_csv('calibrate.csv')
    return df

def plotBefore():
    #fig, axs = plt.subplots(4,4,figsize=(25,28))

    #plt.subplot(2, 1, 1) #two rows, one columns, first graph

    df2 = df
    z = np.polyfit(x=df.loc[:, 'fin temp'], y=df.loc[:, 'true temp'], deg=1)
    p = np.poly1d(z)
    df['trendline'] = p(df.loc[:, 'fin temp'])


    ax = df.plot.scatter(x = 'fin temp', y = 'true temp')
    df['fin calibrated'] = (df['fin temp']*z[0]) + z[1]
    df.set_index("fin temp", inplace=True)
    df.trendline.sort_index(ascending=False).plot(ax=ax, label = 'trendline')
    
    print(df)
    print("\n")
    print("Calibration: ")
    print('y={1:.4f} x + {1:.4f}'.format(z[0],z[1]))
    
    plt.xlim((0,df.index.max()))
    plt.ylim((0,df.index.max()))
    plt.title("Uncalibrated Data")
    plt.show()


    


#main running

#select either manual selection, or importing data into the CSV
df = getCalibrationDataManual()
#df = getCalibrateDataCSV()

print(df)
input()

plotBefore()

