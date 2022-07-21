import serial
import sys
from datetime import date
import time
import pandas as pd

today = date.today().strftime("%m|%d|%y")
SerialPort = str(sys.argv[1]) #Enter your fin serial port name as a command line argument
#For example, $ python3 DataGetter.py /dev/ttyACM0
today = date.today().strftime("%m|%d|%y")
startTime = time.time()


def saveRawData():
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
    df = pd.read_csv('1658269077.csv')
    print(df)

    print(df['    xMag'].astype(str) + ',' + df['    yMag'].astype(str) + ',' + df['    yMag'].astype(str))

saveRawData()

#csvToPd()