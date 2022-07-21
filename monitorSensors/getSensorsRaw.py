import serial
import sys
from datetime import date
import time
import pandas as pd




def saveRawData():
    SerialPort = str(sys.argv[1])  # Enter your fin serial port name as a command line argument
    # For example, $ python3 DataGetter.py /dev/ttyACM0
    startTime = time.time()
    ser = serial.Serial(port=SerialPort, baudrate=115200, timeout=None)

    monitorData = []

    ser.write(('#CLI\r').encode())  # Access CLI through terminal

    ser.write(('#\r').encode())

    time.sleep(2)

    ser.write(('*\r').encode())

    ser.write(('4\r').encode())

    for i in range(300):
        data = ser.readline().decode()
        data = data.strip()
        data = data.split('\t')
        print(data)
        if i > 24:
            monitorData.append(data)

        time.sleep(0.1) #adjust value depending on required Hz

    print(monitorData)
    new_df = pd.DataFrame(monitorData, columns=monitorData[0])
    new_df = new_df.iloc[1:, :]

    print(new_df)
    #print(new_df[['xMag', 'yMag', 'zMag']])

    new_df.to_csv(str(int(time.time())) + '.csv')

    new_df[['    xMag', '    yMag', '    zMag']].to_csv('test.csv', index=False)




def csvToPd():
    # first get all lines from file
    with open('test.csv', 'r') as f:
        lines = f.readlines()

    # remove spaces
    lines = [line.replace(' ', '') for line in lines]

    # finally, write lines in the file
    with open('test.csv', 'w') as f:
        f.writelines(lines[1:])  #[1:] removes title
    #print(df)

    #print(df['    xMag'].astype(str) + ',' + df['    yMag'].astype(str) + ',' + df['    yMag'].astype(str))

#saveRawData()

csvToPd()