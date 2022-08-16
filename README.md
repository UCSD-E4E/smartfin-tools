# intro
Here are some tools to collect, calibrate, download, and view data from the fin.
I will cover them in order of how you will most likely use the tools

## dependencies

numpy, pandas, matplotlib

## download.py

Downloads all data off of the fin through the serial port and puts each session data into a different file. 

Files are in the format: ```[fin serial #]-[file name on fin]-session-data.sfr```.

It also prompts the user to delete the data off the fin if they so choose

command:
```python download.py [serial port the fin is connected to]```

example:
```python download.py /dev/tty.usbmodem142301```

After, you generally want to use decode.py

## decode.py
Decodes the raw data and saves it to the the format [original sfr file name].csv (most useful after using download.py)

command:
```python3 decode.py [sfr file you want to decode]```

example:
```python3 decode.py 200047001750483553353920-000000_temp_00-session-data.sfr```

Note: this data is not calibrated (see calibrate.py for more information)

## calibrate.py
This file will let us take in the raw data and then transform it with the correct calibrations. 

Makes a csv file of the calibrated data (same file name with '_cal-' before it)


command:
```python calibrate.py [file you want to calibrate].csv```

## graph.py
Allows you to graph fin data in a useful, visual way. 

command:
```python graph.py [filename].csv```

example:
```python graph.py _cal-200047001750483553353920-20220804-231057-session-data.csv```

## getCalibrateData.py

This code is used to collect temperature data from both the fin and the SBE-37 with synced timestamps in order to calibrate the fin to the accuracy of the SBE-37.
Creates a file in the directory called "SBETemperatures_[ timestamp ].csv"
After, use download.py and decode.py to get the temperatures off the fin and compare.

To emphasize this, the timestamps you get from the fin and SBETemperatures_[ timestamp ].csv will be synced up with the fin to be able to compare temperature readings.


SETUP:
PLUG IN BOTH FIN AND SBE-37 INTO COMPUTER BEFORE RUNNING COMMAND
MAKE SURE THE FIN IS RESET AND ENTERS CHARGE MODE

RUN COMMAND FORMAT: 
```python3 getCalibrateData.py [SBE-27SI PORT ON DEVICE] [FIN USB PORT ON DEVICE]```

EXAMPLE: 
```python3 getCalibrateData.py  /dev/tty.usbserial14421        /dev/tty.usbmodem23314```

Make sure the firmware on your fin allows you to force a session using the 'S' command in the CLI interface by getting into the fin's CLI and typing '#'.

If you cannot see 'S to force session' try the 'force_session' branch on github and install that firmware for the calibration. 

## dataEndpoint.py

Allows a user to access the data endpoint google sheet

Simply run ```python dataEndpoint.py``` 

Must have the proper credentals in a credentials.json file in the same directory

Example format of credentials.json:
```{"installed":{"client_id":"XXXX","project_id":"XXXX","auth_uri":"XXXX","token_uri":"XXXX","auth_provider_x509_cert_url":"XXXX","client_secret":"XXXX","redirect_uris":["XXXX"]}}```

This file has its own dependencies only used on this file: 

google.auth.transport.requests,
google_auth_oauthlib.flow,
googleapiclient.discovery,
IPython,
pytz,
pickle,

# Still need more info?
message in the smartfin chat

(readme written by Robert O'Brien August 18 2022)
