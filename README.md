# sf-fw-tools
data parser

# sfConvert
`sfConvert` converts between `.sfr`, `.sfp`, and `.csv` formats.
```
sfConvert --help
usage: sfConvert.py [-h] [--input_type {sfr,sfp}] [--output_fp OUTPUT_FP] [--output_type {sfp,csv}] [--no_strip_padding] input

positional arguments:
  input                 filepath to file being converted

options:
  -h, --help            show this help message and exit
  --input_type {sfr,sfp}
  --output_fp OUTPUT_FP, -o OUTPUT_FP
                        filepath to save converted file to (default: {filename}.{output_type})
  --output_type {sfp,csv}
  --no_strip_padding
```

# sfPlotter
`sfPlotter` plots the data streams from `.sfr` files.
```
sfPlotter --help
usage: Smartfin Data Plotter [-h] [--output [OUTPUT]] [csv_fp]

positional arguments:
  csv_fp                filepath to csv being plotted

options:
  -h, --help            show this help message and exit
  --output [OUTPUT], -o [OUTPUT]
                        output directory to store graphs to (default: {csv_filename}_plts)
```

# sfDownloader
`sfDownloader` downloads `.sfr` files directly from the SmartFin.
```
sfDownloader --help
usage: sfDownloader.py [-h] [--delete] [--output_dir OUTPUT_DIR] port

positional arguments:
  port                  path to serial port of fin

options:
  -h, --help            show this help message and exit
  --delete, -d          files deleted from fin if set
  --output_dir OUTPUT_DIR, -o OUTPUT_DIR
                        output directory to put downloaded sfr files (default: current directory)
```

# sfCalibrator
`sfCalibrator` applies calibrations given calibration coefficients and data. Can specify where calibrated data is saved with output_dir argument
```
sfCalibrator --help
usage: sfCalibrator.py [-h] [--output_dir OUTPUT_DIR] data_fp coef_fp

positional arguments:
  data_fp               filepath to csv datafile
  coef_fp               filepath to json coefficients file

options:
  -h, --help            show this help message and exit
  --output_dir OUTPUT_DIR, -o OUTPUT_DIR
                        output directory to save calibrated data to (default: {data_filename}_cal.csv)
```
