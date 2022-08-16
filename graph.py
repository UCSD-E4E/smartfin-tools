import sys
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

#allows you to graph the data downloaded and decoded + calibrated from the fin

#TO USE: 
# command: python graph.py [filename].csv
# e.x.   : python graph.py _cal-200047001750483553353920-20220804-231057-session-data.csv 

#variables
TIME_NEEDED_TO_SETTLE = 240
DEGREE_CHANGE_C_CONSIDERED_SETTLED = 0.2

def plotData(file):
        plotCount = 0

        df = pd.read_csv(file)

        #replace 0s with nan
        df['Temperature'] = df['Temperature'].replace({'0':np.nan, 0:np.nan})

        fig, axs = plt.subplots(3,4,figsize=(25,28))

        axs[0][0].plot(df['timestamp'], df['X Acceleration'])
        axs[0][0].set_title(file + '\n\nX acc vs timestamp')
        axs[0][0].set_ylim(-3,3)
        axs[0][0].set_xlabel("time (s)")
        axs[0][0].set_ylabel("acceleration (g)")
        axs[0][0].axhline(0, color="orange", linestyle="dotted")
        axs[0][0].axhline(1, color="orange", linestyle="dotted", label = '1g')
        axs[0][1].plot(df['timestamp'], df['Y Acceleration'])
        axs[0][1].set_ylim(-3,3)
        axs[0][1].set_title("Y acc vs timestamp")
        axs[0][1].axhline(0, color="orange", linestyle="dotted")
        axs[0][1].axhline(1, color="orange", linestyle="dotted")
        axs[0][1].set_xlabel("time (s)")
        axs[0][1].set_ylabel("acceleration (g)")
        axs[0][2].plot(df['timestamp'], df['Z Acceleration'])
        axs[0][2].set_ylim(-3,3)
        axs[0][2].set_title("Z acc vs timestamp")
        axs[0][2].axhline(0, color="orange", linestyle="dotted")
        axs[0][2].axhline(1, color="orange", linestyle="dotted")
        axs[0][2].set_xlabel("time (s)")
        axs[0][2].set_ylabel("acceleration (g)")

        axs[0][3].plot(df['timestamp'], df['Temperature'])
        axs[0][3].axhline(df['Temperature'].median(), color="orange", linestyle="dotted")
        axs[0][3].set_title("temperature vs timestamp\nMedian: " + str(round(df['Temperature'].median(),2)) + " degrees C")
        axs[0][3].set_xlabel("time (s)")
        axs[0][3].set_ylabel("temperature (C)")


        axs[1][0].plot(df['timestamp'], df['X Angular Velocity'])
        axs[1][0].set_title("X gyro vs timestamp")
        axs[1][0].set_ylim(-300,300) 
        axs[1][0].axhline(0, color="orange", linestyle="dotted")
        axs[1][0].set_xlabel("time (s)")
        axs[1][0].set_ylabel("angular velocity (rad/sec)")
        axs[1][1].plot(df['timestamp'], df['Y Angular Velocity'])
        axs[1][1].set_ylim(-300,300)
        axs[1][1].axhline(0, color="orange", linestyle="dotted")
        axs[1][1].set_title("Y gyro vs timestamp")
        axs[1][1].set_xlabel("time (s)")
        axs[1][1].set_ylabel("angular velocity (rad/sec)")
        axs[1][2].plot(df['timestamp'], df['Z Angular Velocity'])
        axs[1][2].set_ylim(-300,300)
        axs[1][2].set_title("Z gyro vs timestamp")
        axs[1][2].axhline(0, color="orange", linestyle="dotted")
        axs[1][2].set_xlabel("time (s)")
        axs[1][2].set_ylabel("angular velocity (rad/sec)")
        axs[1][3].plot(df['timestamp'], df['Temperature'].diff(periods=1))
        axs[1][3].plot(df['timestamp'], df['Temperature'].diff(periods=300))
        axs[1][3].plot(df['timestamp'], df['Temperature'].diff(periods=-300))
        axs[1][3].set_title("Δ temperature over\nBlue: 1s, Orange: 5min, Green: -5min")
        axs[1][3].axhline(0, color="orange", linestyle="dotted")
        axs[1][3].axhline(DEGREE_CHANGE_C_CONSIDERED_SETTLED, color="orange", linestyle="dotted")
        axs[1][3].axhline(-DEGREE_CHANGE_C_CONSIDERED_SETTLED, color="orange", linestyle="dotted")
        axs[1][3].set_ylim(-1,1)
        axs[1][3].set_xlabel("time (s)")
        axs[1][3].set_ylabel("Δ temperature (C)")

        axs[2][0].scatter( df['timestamp'], df['X Magnetic Field'])
        axs[2][0].set_ylim(-6000,6000)
        axs[2][0].set_title("X mag vs timestamp")
        axs[2][0].set_xlabel("time (s)")
        axs[2][0].set_ylabel("magnetic field strength (nT)")
        axs[2][1].scatter(df['timestamp'], df['Y Magnetic Field'])
        axs[2][1].set_ylim(-6000,6000)
        axs[2][1].set_title("Y mag vs timestamp")
        axs[2][1].set_xlabel("time (s)")
        axs[2][1].set_ylabel("magnetic field strength (nT)")
        axs[2][2].scatter(df['timestamp'], df['Z Magnetic Field'])
        axs[2][2].set_ylim(-6000,6000)
        axs[2][2].set_title("Z mag vs timestamp")
        axs[2][2].set_xlabel("time (s)")
        axs[2][2].set_ylabel("magnetic field strength (nT)")

        df['Water Detect'] = df['Water Detect'].replace({np.nan:0.1})
        axs[2][3].scatter(df['timestamp'], df['Water Detect'] > 0)
        axs[2][3].set_title("timestamp vs water detect")
        axs[2][3].set_xlabel("time (s)")
        axs[2][3].set_ylabel("water detected (1/0)")

        plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)

        plt.savefig(file[:-3] + "png")
        plotCount+=1

if __name__ == "__main__":
        plotData(sys.argv[1])

        print("Graphing complete.")