'''Smartfin Plotting Tool
'''
import argparse
import base64
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import pandas as pd

import smartfin_tools.decoder
from smartfin_tools import __version__


def plotFile(fileName: Path, output_dir: Path, *, decoder: Callable[[str], bytes] = base64.urlsafe_b64decode):
    ensembles = []
    with open(fileName, 'r', encoding='utf-8') as handle:
        for record in handle:
            data = decoder(record)
            ensembles.extend(smartfin_tools.decoder.decode_packet(data))

    df = pd.DataFrame(ensembles)
    df = smartfin_tools.decoder.convert_to_si(df)

    plot_dir = output_dir / fileName.stem
    plot_dir.mkdir(parents=True, exist_ok=True)

    plt.scatter(df.index, df['timestamp'])
    plt.xlabel('Ensemble Number by decode order')
    plt.ylabel('Timestamp (s)')
    plt.title('Time vs Ensemble Number')
    plt.grid()
    plt.savefig(plot_dir / 'EnsembleNumber.png')
    plt.close()

    plt.scatter(df['timestamp'], df['Temperature (C)'])
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (C)')
    plt.title("Temperature vs Time")
    plt.grid()
    plt.savefig(plot_dir / "Temperature.png")
    plt.close()

    plt.scatter(df['timestamp'], df['Water Detect'])
    plt.xlabel('Time (s)')
    plt.ylabel('Water Detect Reading')
    plt.title('Water Detect Reading')
    plt.grid()
    plt.savefig(plot_dir / "WaterDetect.png")
    plt.close()

    plt.scatter(df['timestamp'], df['dataType'])
    plt.xlabel('Time (s)')
    plt.ylabel('Data Type')
    plt.title('Data Types')
    plt.grid()
    plt.savefig(plot_dir / "DataTypes.png")
    plt.close()

    if "X Acceleration (m/s^2)" in df.columns:
        plt.scatter(df['timestamp'], df['X Acceleration (m/s^2)'])
        plt.xlabel('Time (s)')
        plt.ylabel('Acceleration (m/s^2)')
        plt.title('X Acceleration')
        plt.grid()
        plt.savefig(plot_dir / 'Acceleration_x.png')
        plt.close()

    if "Y Acceleration (m/s^2)" in df.columns:
        plt.scatter(df['timestamp'], df['Y Acceleration (m/s^2)'])
        plt.xlabel('Time (s)')
        plt.ylabel('Acceleration (m/s^2)')
        plt.title('Y Acceleration')
        plt.grid()
        plt.savefig(plot_dir / 'Acceleration_y.png')
        plt.close()

    if "Z Acceleration (m/s^2)" in df.columns:
        plt.scatter(df['timestamp'], df['Z Acceleration (m/s^2)'])
        plt.xlabel('Time (s)')
        plt.ylabel('Acceleration (m/s^2)')
        plt.title('Z Acceleration')
        plt.grid()
        plt.savefig(plot_dir / 'Acceleration_z.png')
        plt.close()

    if "X Angular Velocity (deg/s)" in df.columns:
        plt.scatter(df['timestamp'], df['X Angular Velocity (deg/s)'])
        plt.xlabel('Time (s)')
        plt.ylabel('Angular Velocity (deg/s)')
        plt.title('X Angular Velocity')
        plt.grid()
        plt.savefig(plot_dir / 'AngularVel_x.png')
        plt.close()

    if "Y Angular Velocity (deg/s)" in df.columns:
        plt.scatter(df['timestamp'], df['Y Angular Velocity (deg/s)'])
        plt.xlabel('Time (s)')
        plt.ylabel('Angular Velocity (deg/s)')
        plt.title('Y Angular Velocity')
        plt.grid()
        plt.savefig(plot_dir / 'AngularVel_y.png')
        plt.close()

    if "Z Angular Velocity (deg/s)" in df.columns:
        plt.scatter(df['timestamp'], df['Z Angular Velocity (deg/s)'])
        plt.xlabel('Time (s)')
        plt.ylabel('Angular Velocity (deg/s)')
        plt.title('Z Angular Velocity')
        plt.grid()
        plt.savefig(plot_dir / 'AngularVel_z.png')
        plt.close()

    if "X Magnetic Field (uT)" in df.columns:
        plt.scatter(df['timestamp'], df['X Magnetic Field (uT)'])
        plt.xlabel('Time (s)')
        plt.ylabel('Magnetic Field Strength (uT)')
        plt.title('X Magnetic Field')
        plt.grid()
        plt.savefig(plot_dir / 'Magfield_x.png')
        plt.close()

    if "Y Magnetic Field (uT)" in df.columns:
        plt.scatter(df['timestamp'], df['Y Magnetic Field (uT)'])
        plt.xlabel('Time (s)')
        plt.ylabel('Magnetic Field Strength (uT)')
        plt.title('Y Magnetic Field')
        plt.grid()
        plt.savefig(plot_dir / 'Magfield_y.png')
        plt.close()

    if "Z Magnetic Field (uT)" in df.columns:
        plt.scatter(df['timestamp'], df['Z Magnetic Field (uT)'])
        plt.xlabel('Time (s)')
        plt.ylabel('Magnetic Field Strength (uT)')
        plt.title('Z Magnetic Field')
        plt.grid()
        plt.savefig(plot_dir / 'Magfield_z.png')
        plt.close()

    if "battery" in df.columns:
        plt.scatter(df['timestamp'], df['battery'])
        plt.xlabel('Time (s)')
        plt.ylabel('Battery Voltage (mV)')
        plt.title('Battery Voltage')
        plt.grid()
        plt.savefig(plot_dir / 'Battery.png')
        plt.close()


def main():
    parser = argparse.ArgumentParser(
        description=f'Smartfin Data Plotter {__version__}'
    )
    parser.add_argument('sfr_file', default=None, type=Path)
    parser.add_argument('output', default=Path('.'), type=Path)
    parser.add_argument(
        '-e', '--encoding', choices=['base85', 'base64', 'base64url'], default='base64url')
    args = parser.parse_args()
    output_dir: Path = args.output
    if args.sfr_file:
        path = args.sfr_file
    else:
        print("Enter path:")
        path = Path(input())

    if not path.is_file():
        print("Not a file!")
        return
    print(f'Graphing {path.as_posix()}')

    if args.encoding == 'base64url':
        decoder = base64.urlsafe_b64decode
    elif args.encoding == 'base64':
        decoder = base64.b64decode
    elif args.encoding == 'base85':
        decoder = base64.b85decode
    else:
        raise NotImplementedError(f"Unknown encoding {args.encoding}")

    plotFile(path, output_dir, decoder=decoder)


if __name__ == "__main__":
    main()
