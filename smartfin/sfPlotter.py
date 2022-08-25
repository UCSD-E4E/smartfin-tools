#!/usr/bin/env python3

from pathlib import Path
import decoder
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
import argparse

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


def main():
    parser = argparse.ArgumentParser("Smartfin Data Plotter")
    parser.add_argument('csv_fp', default=None, nargs='?')
    parser.add_argument('output', default=None, nargs='?')
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