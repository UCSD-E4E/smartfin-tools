*NOTE - make sure you are in the right path (e.g. ~/Documents/E4E_SmartFin/smartfin-tools)

How to use serial Port
1)use command

python3 robPlot.py /dev/tty.usbmodem*

2)

enter a name for the graph data

3)

type "S" then enter while connected to the fin via serial port


how to upload by file

1) put the raw data in a file named 

07|11|22session-data.sfr

but with todays date

2)use command

python3 robPlot.py /dev/tty.usbmodem*

3) enter a name, press enter

4) type F, press enter

how to use the sheet getter (cloud)

1) do not use it yet


HOW TO JUST DOWNLOAD THE DATA (NOT DECODE)

1) use command

python3 serialPort.py /dev/tty.usbmodem*

and follow prompts. files will be saved to the save directory

