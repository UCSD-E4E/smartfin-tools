#!/usr/bin/env python3

from pathlib import Path
import decoder
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import argparse

DEGREE_CHANGE_C_CONSIDERED_SETTLED = 0.2

def plotFile(fileName:str, output_dir:str)->str:
    df = pd.read_csv(fileName)
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    plt.scatter(df.index, df['timestamp'])
    plt.xlabel('Ensemble Number by decode order')
    plt.ylabel('Timestamp (s)')
    plt.title('Time vs Ensemble Number')
    plt.grid()
    plt.savefig(os.path.join(output_dir, 'EnsembleNumber.png'))
    plt.close()

    plt.scatter(df['timestamp'], df['Temperature'])
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (C)')
    plt.title("Temperature vs Time")
    plt.grid()
    plt.savefig(os.path.join(output_dir, "Temperature.png"))
    plt.close()

    plt.scatter(df['timestamp'], df['Water Detect'])
    plt.xlabel('Time (s)')
    plt.ylabel('Water Detect Reading')
    plt.title('Water Detect Reading')
    plt.grid()
    plt.savefig(os.path.join(output_dir, "WaterDetect.png"))
    plt.close()

    plt.scatter(df['timestamp'], df['dataType'])
    plt.xlabel('Time (s)')
    plt.ylabel('Data Type')
    plt.title('Data Types')
    plt.grid()
    plt.savefig(os.path.join(output_dir, "DataTypes.png"))
    plt.close()
    
    if "X Acceleration" in df.columns:
        plt.scatter(df['timestamp'], df['X Acceleration'])
        plt.xlabel('Time (s)')
        plt.ylabel('Acceleration (g)')
        plt.title('X Acceleration')
        plt.grid()
        plt.savefig(os.path.join(output_dir, 'Acceleration_x.png'))
        plt.close()

    if "Y Acceleration" in df.columns:
        plt.scatter(df['timestamp'], df['Y Acceleration'])
        plt.xlabel('Time (s)')
        plt.ylabel('Acceleration (g)')
        plt.title('Y Acceleration')
        plt.grid()
        plt.savefig(os.path.join(output_dir, 'Acceleration_y.png'))
        plt.close()

    if "Z Acceleration" in df.columns:
        plt.scatter(df['timestamp'], df['Z Acceleration'])
        plt.xlabel('Time (s)')
        plt.ylabel('Acceleration (g)')
        plt.title('Z Acceleration')
        plt.grid()
        plt.savefig(os.path.join(output_dir, 'Acceleration_z.png'))
        plt.close()

    if "X Angular Velocity" in df.columns:
        plt.scatter(df['timestamp'], df['X Angular Velocity'])
        plt.xlabel('Time (s)')
        plt.ylabel('Angular Velocity (deg/s)')
        plt.title('X Angular Velocity')
        plt.grid()
        plt.savefig(os.path.join(output_dir, 'AngularVel_x.png'))
        plt.close()

    if "Y Angular Velocity" in df.columns:
        plt.scatter(df['timestamp'], df['Y Angular Velocity'])
        plt.xlabel('Time (s)')
        plt.ylabel('Angular Velocity (deg/s)')
        plt.title('Y Angular Velocity')
        plt.grid()
        plt.savefig(os.path.join(output_dir, 'AngularVel_y.png'))
        plt.close()

    if "Z Angular Velocity" in df.columns:
        plt.scatter(df['timestamp'], df['Z Angular Velocity'])
        plt.xlabel('Time (s)')
        plt.ylabel('Angular Velocity (deg/s)')
        plt.title('Z Angular Velocity')
        plt.grid()
        plt.savefig(os.path.join(output_dir, 'AngularVel_z.png'))
        plt.close()

    if "X Magnetic Field" in df.columns:
        plt.scatter(df['timestamp'], df['X Magnetic Field'])
        plt.xlabel('Time (s)')
        plt.ylabel('Magnetic Field Strength (uT)')
        plt.title('X Magnetic Field')
        plt.grid()
        plt.savefig(os.path.join(output_dir, 'Magfield_x.png'))
        plt.close()

    if "Y Magnetic Field" in df.columns:
        plt.scatter(df['timestamp'], df['Y Magnetic Field'])
        plt.xlabel('Time (s)')
        plt.ylabel('Magnetic Field Strength (uT)')
        plt.title('Y Magnetic Field')
        plt.grid()
        plt.savefig(os.path.join(output_dir, 'Magfield_y.png'))
        plt.close()

    if "Z Magnetic Field" in df.columns:
        plt.scatter(df['timestamp'], df['Z Magnetic Field'])
        plt.xlabel('Time (s)')
        plt.ylabel('Magnetic Field Strength (uT)')
        plt.title('Z Magnetic Field')
        plt.grid()
        plt.savefig(os.path.join(output_dir, 'Magfield_z.png'))
        plt.close()

    if "battery" in df.columns:
        plt.scatter(df['timestamp'], df['battery'])
        plt.xlabel('Time (s)')
        plt.ylabel('Battery Voltage (mV)')
        plt.title('Battery Voltage')
        plt.grid()
        plt.savefig(os.path.join(output_dir, 'Battery.png'))
        plt.close()
    
    if "Z Magnetic Field" in df.columns and "X Magnetic Field" in df.columns:
        plotHeadings(getHeading(df), df["timestamp"], output_dir)
        
    plotConsolidated(df, output_dir)

def plotConsolidated(df, output_dir):
    fig, axs = plt.subplots(3,4,figsize=(25,28))

    if 'X Acceleration' in df.columns:
        axs[0][0].plot(df['timestamp'], df['X Acceleration'])
        axs[0][0].set_title(output_dir + '\n\nX acc vs timestamp')
        axs[0][0].set_ylim(-3,3)
        axs[0][0].set_xlabel("time (s)")
        axs[0][0].set_ylabel("acceleration (g)")
        axs[0][0].axhline(0, color="orange", linestyle="dotted")
        axs[0][0].axhline(1, color="orange", linestyle="dotted", label = '1g')
        
    if 'Y Acceleration' in df.columns:
        axs[0][1].plot(df['timestamp'], df['Y Acceleration'])
        axs[0][1].set_ylim(-3,3)
        axs[0][1].set_title("Y acc vs timestamp")
        axs[0][1].axhline(0, color="orange", linestyle="dotted")
        axs[0][1].axhline(1, color="orange", linestyle="dotted")
        axs[0][1].set_xlabel("time (s)")
        axs[0][1].set_ylabel("acceleration (g)")
        
    if 'Z Acceleration' in df.columns:
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

    if 'X Angular Velocity' in df.columns:
        axs[1][0].plot(df['timestamp'], df['X Angular Velocity'])
        axs[1][0].set_title("X gyro vs timestamp")
        axs[1][0].set_ylim(-300,300) 
        axs[1][0].axhline(0, color="orange", linestyle="dotted")
        axs[1][0].set_xlabel("time (s)")
        axs[1][0].set_ylabel("angular velocity (rad/sec)")
        
    if 'Y Angular Velocity' in df.columns:
        axs[1][1].plot(df['timestamp'], df['Y Angular Velocity'])
        axs[1][1].set_ylim(-300,300)
        axs[1][1].axhline(0, color="orange", linestyle="dotted")
        axs[1][1].set_title("Y gyro vs timestamp")
        axs[1][1].set_xlabel("time (s)")
        axs[1][1].set_ylabel("angular velocity (rad/sec)")
        
    if 'Z Angular Velocity' in df.columns:
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

    if 'X Magnetic Field' in df.columns:
        axs[2][0].scatter( df['timestamp'], df['X Magnetic Field'])
        axs[2][0].set_ylim(-6000,6000)
        axs[2][0].set_title("X mag vs timestamp")
        axs[2][0].set_xlabel("time (s)")
        axs[2][0].set_ylabel("magnetic field strength (nT)")
        
    if 'Y Magnetic Field' in df.columns:
        axs[2][1].scatter(df['timestamp'], df['Y Magnetic Field'])
        axs[2][1].set_ylim(-6000,6000)
        axs[2][1].set_title("Y mag vs timestamp")
        axs[2][1].set_xlabel("time (s)")
        axs[2][1].set_ylabel("magnetic field strength (nT)")
        
    if 'Z Magnetic Field' in df.columns:
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

    plt.savefig(os.path.join(output_dir, "ConsolidatedGraphs.png"))

def getHeading(df_data):
    z_arr = df_data.loc[:,"Z Magnetic Field"].to_numpy()
    x_arr = df_data.loc[:,"X Magnetic Field"].to_numpy()
    
    return np.arctan2(z_arr, x_arr) * 180 / np.pi

def plotHeadings(heading_arr, timestamps, output_dir):
    plt.scatter(timestamps, heading_arr, s=10) #Cartesian Graph
    plt.title('Heading vs Time')
    plt.xlabel('Time')
    plt.ylabel('Degrees')
    plt.savefig(os.path.join(output_dir, "CartesianHeadings.png"), dpi=300)

    plt.clf()

    r = timestamps #Polar graph
    theta = (heading_arr / 180) * np.pi + np.pi / 2
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    labels = [item.get_text() for item in ax.get_xticklabels()]
    labels[0], labels[1], labels[2], labels[3], \
    labels[4], labels[5], labels[6], labels[7] = 'E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'
    ax.set_xticklabels(labels)
    ax.set_yticklabels([])
    ax.scatter(theta, r, marker=',', s=1, cmap = 'winter')
    plt.savefig(os.path.join(output_dir, "PolarHeadings.png"), dpi=1000)
        
        
def main():
    parser = argparse.ArgumentParser("Smartfin Data Plotter")
    parser.add_argument('csv_fp', default=None, nargs='?', help="filepath to csv being plotted")
    parser.add_argument('--output', '-o', default=None, nargs='?', help="output directory to store graphs to (default: {csv_filename}_plts)")
    args = parser.parse_args()
    
    if args.csv_fp:
        path = args.csv_fp
    else:
        print("Enter path:")
        path = input()
    
    if not os.path.isfile(path):
        print("Not a file!")
        return
    print("Graphing %s" % path)
    
    if args.output:
        output_dir = args.output
    else:
        output_dir = "{}_plts".format(os.path.splitext(args.csv_fp)[0])
    plotFile(path, output_dir)

if __name__ == "__main__":
    main()