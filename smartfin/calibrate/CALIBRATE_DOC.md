# sf-calibrate-tools
calibration tools

# calibrate_acc
`calibrate_acc` calibrates the accelerometer. Can specify what json file to save calibration to and how long calibration period is for each axii. Calibration is performed by holding fin still in all 6 orientations.
```
calibrate_acc.py --help
usage: calibrate_acc.py [-h] [--output_dir OUTPUT_DIR] [--cal_per CAL_PER] port

positional arguments:
  port                  path to serial port of fin

options:
  -h, --help            show this help message and exit
  --output_dir OUTPUT_DIR, -o OUTPUT_DIR
                        json file to output calibration coefficients to (default: calibrations.json)
  --cal_per CAL_PER, -p CAL_PER
                        calibration period per orientation (s) (default: 10)
```

# calibrate_gyro
`calibrate_gyro` calibrates the gyroscope. Can specify what json file to save calibration to and how long calibration period is. Calibration is performed by keeping fin completely still for the length of the calbiration period (zero calibration).
```
calibrate_gyro --help
usage: calibrate_gyro.py [-h] [--output_dir OUTPUT_DIR] [--cal_per CAL_PER] port

positional arguments:
  port                  path to serial port of fin

options:
  -h, --help            show this help message and exit
  --output_dir OUTPUT_DIR, -o OUTPUT_DIR
                        json file to output calibration coefficients to (default: calibrations.json)
  --cal_per CAL_PER, -p CAL_PER
                        calibration period (s) (default: 60)
```

# calibrate_mag
`calibrate_mag` calibrates the magnetometer. Can specify what json file to save calibration to. Calibration is performed by moving fin around until live plot shows a complete sphere. Data collection period is ended with `ctrl-c`.
```
calibrate_mag --help
usage: calibrate_mag.py [-h] [--output_dir OUTPUT_DIR] port

positional arguments:
  port                  path to serial port of fin

options:
  -h, --help            show this help message and exit
  --output_dir OUTPUT_DIR, -o OUTPUT_DIR
                        json file to output calibration coefficients to (default: calibrations.json)
```
