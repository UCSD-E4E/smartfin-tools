# sf-fw-tools
data parser

# sfConvert
`sfConvert` converts between `.sfr`, `.sfp`, and `.csv` formats.
```
sfConvert --help
usage: sfConvert [-h] [--input_type {sfr,sfp}] [--output_type {sfp,csv}] [--no_strip_padding] input output

positional arguments:
  input
  output

optional arguments:
  -h, --help            show this help message and exit
  --input_type {sfr,sfp}
  --output_type {sfp,csv}
  --no_strip_padding
```

# sfPlotter
`sfPlotter` plots the data streams from `.sfr` files.
```
sfPlotter --help
usage: Smartfin Data Plotter [-h] [sfr_file] [output]

positional arguments:
  sfr_file
  output

optional arguments:
  -h, --help  show this help message and exit
```

# sfDownloader
`sfDownloader` downloads `.sfr` files directly from the SmartFin.
```
sfDownloader --help
usage: sfDownloader [-h] [--delete] [--output_dir OUTPUT_DIR] port

positional arguments:
  port

optional arguments:
  -h, --help            show this help message and exit
  --delete, -d
  --output_dir OUTPUT_DIR, -o OUTPUT_DIR
```