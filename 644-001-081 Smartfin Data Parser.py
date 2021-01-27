import sys
import base64
import csv
# import matplotlib
import time
from math import pow, sqrt 

TEMP_DATA_TYPE = 1
IMU_DATA_TYPE = 2
GPS_DATA_TYPE = 3
TEMP_IMU_DATA_TYPE = 4
TEMP_GPS_DATA_TYPE = 5
TEMP_IMU_GPS_DATA_TYPE = 6
BATT_DATA_TYPE = 7
TEMP_EPOCH_DATA_TYPE = 8
IMUx3_DATA_TYPE = 9
TEMP_IMUx3_DATA_TYPE = 10
TEMP_IMUx3_GPS_DATA_TYPE = 11
TEXT_DATA_TYPE = 15

CREATE_TMP_CAL_CSV = False
CSV_FILENAME = 'test.csv'
imu_temp_enabled = False
CREATE_TEMP_LOG_CSV = False
CREATE_IMU_LOG = True

# Accelerometer max g
ACCELEROMETER_MAX = 2
GYROSCOPE_MAX = 250
MAG_CONVERSION = 0.15

def vector_magnitude(x: float, y: float, z: float) -> float:
    """
    Return the magnitue of the vector with the provided x, y, and z coordnates.
    :param x:
    :param y:
    :param z:
    :return:
    """
    return sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2))

if len(sys.argv) != 2:
    print("Usage: " + sys.argv[0] + " <filename>")
    exit()

try:
    f = open (sys.argv[1], "r")
except:
    print("Can't open " + sys.argv[1])
    exit()

try:
    data_to_decode = f.read();
except:
    print("Can't read " + sys.argv[1])
    exit()

print("Encoded:")
print(data_to_decode)
decoded = base64.b85decode(data_to_decode)
print("Decoded:")
print(decoded)
print()

with open(CSV_FILENAME, 'w', newline='') as csvfile:
    csvfileWriter = csv.writer(csvfile)

    if CREATE_IMU_LOG:
        csvfileWriter.writerow(
            ["Time",
             "Acceleration X (g)",
             "Acceleration Y (g)",
             "Acceleration Z (g)",
             "Acceleration Total (g)",
             "Gyro X (dps)",
             "Gyro Y (dps)",
             "Gyro Z (dps)",
             "Gyro Total (dps)",
             "Magnetometer X (uT)",
             "Magnetometer Y (uT)",
             "Magnetometer Z (uT)",
             "Magnetometer Total (uT)",
             ])

    i = 0
    j = 0
    while(i < (len(decoded))):
        #type = (decoded[i]>>4)
        type = (decoded[i]&0x0F)

        # deal with padding if it exists
        if (type == 0):
            type_name = 'Padding'
            i = i + 1
            print("type = " + str(type_name))
            print()
            continue

        # grab time (wait until after dealing with padding)
        #time = (((decoded[i] & 0x0F) << 16) + (decoded[i+1] << 8) + decoded[i+2])/10.0
        time = (((decoded[i] >> 4) << 16) + (decoded[i+1] << 8) + decoded[i+2])/10.0


        # decode data type

        if (type == TEMP_DATA_TYPE):
            type_name = 'TEMP'
            if imu_temp_enabled:
                temp = (((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) / 333.87) + 21.0
            else:
                temp = ((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) * 0.0078125

            if (temp < 0):
                temp = temp + 100.0
                inWater = False
            else:
                inWater = True
            print("type = " + str(type_name))
            print("time = " + str(time) + " sec")
            print("temp = " + str(temp) + " C")
            print("In Water? = " + str(inWater))
            print("")
            i = i + 5

        elif (type == IMU_DATA_TYPE):
            type_name = 'IMU'
            Ax = ((-128 * (decoded[i+3] >> 7)) +  (decoded[i+3] & 0x7F)) * 2.0/128
            Ay = ((-128 * (decoded[i+4] >> 7)) +  (decoded[i+4] & 0x7F)) * 2.0/128
            Az = ((-128 * (decoded[i+5] >> 7)) +  (decoded[i+5] & 0x7F)) * 2.0/128

            print("type = " + str(type_name))
            print("time = " + str(time) + " sec")
            print("Ax = " + str(Ax) + " g")
            print("Ay = " + str(Ay) + " g")
            print("Az = " + str(Az) + " g")
            print("")
            i = i + 6

        elif (type == TEMP_IMU_DATA_TYPE):
            type_name = 'TEMP+IMU'
            if imu_temp_enabled:
                temp = (((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) / 333.87) + 21.0
            else:
                temp = ((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) * 0.0078125

            if (temp < 0):
                temp = temp + 100.0
                inWater = False
            else:
                inWater = True

            Ax = ((-128 * (decoded[i+5] >> 7)) +  (decoded[i+5] & 0x7F)) * 2.0/128
            Ay = ((-128 * (decoded[i+6] >> 7)) +  (decoded[i+6] & 0x7F)) * 2.0/128
            Az = ((-128 * (decoded[i+7] >> 7)) +  (decoded[i+7] & 0x7F)) * 2.0/128

            print("type = " + str(type_name))
            print("time = " + str(time) + " sec")
            print("temp = " + str(temp) + " C")
            print("In Water? = " + str(inWater))
            print("Ax = " + str(Ax) + " g")
            print("Ay = " + str(Ay) + " g")
            print("Az = " + str(Az) + " g")
            print("")
            i = i + 8

        elif (type == TEMP_IMU_GPS_DATA_TYPE):
            type_name = 'TEMP+IMU+GPS'
            if imu_temp_enabled:
                temp = (((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) / 333.87) + 21.0
            else:
                temp = ((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) * 0.0078125

            if (temp < 0):
                temp = temp + 100.0
                inWater = False
            else:
                inWater = True

            Ax = ((-128 * (decoded[i+5] >> 7)) +  (decoded[i+5] & 0x7F)) * 2.0/128
            Ay = ((-128 * (decoded[i+6] >> 7)) +  (decoded[i+6] & 0x7F)) * 2.0/128
            Az = ((-128 * (decoded[i+7] >> 7)) +  (decoded[i+7] & 0x7F)) * 2.0/128

            lat = ((-256*256*256*128 * (decoded[i+8] >> 7)) + ((decoded[i+8] & 0x7F) << 24) + ((decoded[i+9]) << 16) + ((decoded[i+10]) << 8) + ((decoded[i+11])))/1000000.0
            lng = ((-256*256*256*128 * (decoded[i+12] >> 7)) + ((decoded[i+12] & 0x7F) << 24) + ((decoded[i+13]) << 16) + ((decoded[i+14]) << 8) + ((decoded[i+15])))/1000000.0
            print("type = " + str(type_name))
            print("time = " + str(time) + " sec")
            print("temp = " + str(temp) + " C")
            print("In Water? = " + str(inWater))
            print("Ax = " + str(Ax) + " g")
            print("Ay = " + str(Ay) + " g")
            print("Az = " + str(Az) + " g")
            print("lat = " + str(lat) + " deg")
            print("lng = " + str(lng) + " deg")
            print("")
            i = i + 16

        elif (type == TEXT_DATA_TYPE):
            type_name = 'TEXT'
            # get text string length
            temp = decoded[i+3]

            print("type = " + str(type_name))
            print("time = " + str(time) + " sec")
            print("text = " + str(decoded[i+4: i+4+temp]))
            print("")
            i = i + 4 + temp

        elif (type == BATT_DATA_TYPE):
            type_name = 'BATT INFO'
            # get text string length
            batt_mv = (decoded[i+3] << 8) + decoded[i+4]

            print("type = " + str(type_name))
            print("time = " + str(time) + " sec")
            print("batt = " + str(batt_mv / 1000.0) + " V")
            print("")
            i = i + 5

        elif (type == TEMP_EPOCH_DATA_TYPE):
            type_name = 'TEMP+EPOCH'
            if imu_temp_enabled:
                temp = (((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) / 333.87) + 21.0
            else:
                temp = ((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) * 0.0078125

            if (temp < 0):
                temp = temp + 100.0
                inWater = False
            else:
                inWater = True
            epochTime = ((256*256*256) * (decoded[i+5] & 0xFF)) + ((256*256) * (decoded[i+6] & 0xFF)) + ((256) * (decoded[i+7] & 0xFF)) + (decoded[i+8] & 0xFF)

            # log stuff to csv file
            if (CREATE_TMP_CAL_CSV):
                # excel row counter
                j=j+1
                # prints out a row containing the cycle time, epoch time, temp, and then UTC HH:MM:SS timestamp (convert excel sheet to time format to see it)
                csvfileWriter.writerow([str(time), str(epochTime), str(temp), ('=(((B' + str(j) + '/60)/60)/24)+DATE(1970,1,1)')])
            print("type = " + str(type_name))
            print("time = " + str(time) + " sec")
            print("temp = " + str(temp) + " C")
            print("In Water? = " + str(inWater))
            print("EPOCH time = " + str(epochTime))
            print("")
            i = i + 9

        elif (type == IMUx3_DATA_TYPE):
            type_name = 'IMUx3'

            Ax = float((decoded[i + 5] << 8) + decoded[i + 6])
            Ay = float((decoded[i + 7] << 8) + decoded[i + 8])
            Az = float((decoded[i + 9] << 8) + decoded[i + 10])

            if Ax >= 0x8000:
                Ax -= 0x10000
            if Ay >= 0x8000:
                Ay -= 0x10000
            if Az >= 0x8000:
                Az -= 0x10000

            Ax /= float(0x8000 / ACCELEROMETER_MAX)
            Ay /= float(0x8000 / ACCELEROMETER_MAX)
            Az /= float(0x8000 / ACCELEROMETER_MAX)

            Gx = float((decoded[i + 11] << 8) + decoded[i + 12])
            Gy = float((decoded[i + 13] << 8) + decoded[i + 14])
            Gz = float((decoded[i + 15] << 8) + decoded[i + 16])

            if Gx >= 0x8000:
                Gx -= 0x10000
            if Gy >= 0x8000:
                Gy -= 0x10000
            if Gz >= 0x8000:
                Gz -= 0x10000

            Gx /= float(0x8000 / GYROSCOPE_MAX)
            Gy /= float(0x8000 / GYROSCOPE_MAX)
            Gz /= float(0x8000 / GYROSCOPE_MAX)

            Mx = float((decoded[i + 18] << 8) + decoded[i + 17])
            My = float((decoded[i + 20] << 8) + decoded[i + 19])
            Mz = float((decoded[i + 22] << 8) + decoded[i + 21])

            if Mx >= 0x8000:
                Mx -= 0x10000
            if My >= 0x8000:
                My -= 0x10000
            if Mz >= 0x8000:
                Mz -= 0x10000

            Mx *= MAG_CONVERSION
            My *= MAG_CONVERSION
            Mz *= MAG_CONVERSION

            if CREATE_IMU_LOG:
                csvfileWriter.writerow(
                    [str(time),
                     Ax, Ay, Az, vector_magnitude(Ax, Ay, Az),
                     Gx, Gy, Gz, vector_magnitude(Gx, Gy, Gz),
                     Mx, My, Mz, vector_magnitude(Mx, My, Mz),])

            print("type = " + str(type_name))
            print("time = " + str(time) + " sec")
            print("Ax = " + str(Ax) + " g")
            print("Ay = " + str(Ay) + " g")
            print("Az = " + str(Az) + " g")
            print("Gx = " + str(Gx) + " dps")
            print("Gy = " + str(Gy) + " dps")
            print("Gz = " + str(Gz) + " dps")
            print("Mx = " + str(Mx) + " uT")
            print("My = " + str(My) + " uT")
            print("Mz = " + str(Mz) + " uT")
            print("")
            i = i + 3 + 3*(2*3)

        elif (type == TEMP_IMUx3_DATA_TYPE):
            type_name = 'TEMP+IMUx3'
            if imu_temp_enabled:
                temp = (((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) / 333.87) + 21.0
            else:
                temp = ((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) * 0.0078125

            if (temp < 0):
                temp = temp + 100.0
                inWater = False
            else:
                inWater = True

            Ax = float((decoded[i + 5] << 8) + decoded[i + 6])
            Ay = float((decoded[i + 7] << 8) + decoded[i + 8])
            Az = float((decoded[i + 9] << 8) + decoded[i + 10])

            if Ax >= 0x8000:
                Ax -= 0x10000
            if Ay >= 0x8000:
                Ay -= 0x10000
            if Az >= 0x8000:
                Az -= 0x10000

            Ax /= float(0x8000 / ACCELEROMETER_MAX)
            Ay /= float(0x8000 / ACCELEROMETER_MAX)
            Az /= float(0x8000 / ACCELEROMETER_MAX)

            Gx = float((decoded[i + 11] << 8) + decoded[i + 12])
            Gy = float((decoded[i + 13] << 8) + decoded[i + 14])
            Gz = float((decoded[i + 15] << 8) + decoded[i + 16])

            if Gx >= 0x8000:
                Gx -= 0x10000
            if Gy >= 0x8000:
                Gy -= 0x10000
            if Gz >= 0x8000:
                Gz -= 0x10000

            Gx /= float(0x8000 / GYROSCOPE_MAX)
            Gy /= float(0x8000 / GYROSCOPE_MAX)
            Gz /= float(0x8000 / GYROSCOPE_MAX)

            Mx = float((decoded[i + 18] << 8) + decoded[i + 17])
            My = float((decoded[i + 20] << 8) + decoded[i + 19])
            Mz = float((decoded[i + 22] << 8) + decoded[i + 21])

            if Mx >= 0x8000:
                Mx -= 0x10000
            if My >= 0x8000:
                My -= 0x10000
            if Mz >= 0x8000:
                Mz -= 0x10000

            Mx *= MAG_CONVERSION
            My *= MAG_CONVERSION
            Mz *= MAG_CONVERSION

            if CREATE_IMU_LOG:
                csvfileWriter.writerow(
                    [str(time),
                     Ax, Ay, Az, vector_magnitude(Ax, Ay, Az),
                     Gx, Gy, Gz, vector_magnitude(Gx, Gy, Gz),
                     Mx, My, Mz, vector_magnitude(Mx, My, Mz),])

            # log stuff to csv file
            if (CREATE_TEMP_LOG_CSV):
                # excel row counter
                j = j + 1
                # prints out a row containing the cycle time and temp
                csvfileWriter.writerow(
                    [str(time), str(temp)])

            print("type = " + str(type_name))
            print("time = " + str(time) + " sec")
            print("temp = " + str(temp) + " C")
            print("In Water? = " + str(inWater))
            print("Ax = " + str(Ax) + " g")
            print("Ay = " + str(Ay) + " g")
            print("Az = " + str(Az) + " g")
            print("Gx = " + str(Gx) + " dps")
            print("Gy = " + str(Gy) + " dps")
            print("Gz = " + str(Gz) + " dps")
            print("Mx = " + str(Mx) + " uT")
            print("My = " + str(My) + " uT")
            print("Mz = " + str(Mz) + " uT")
            print("")
            i = i + 3 + 2 + 3*(2*3)

        elif (type == TEMP_IMUx3_GPS_DATA_TYPE):
            type_name = 'TEMP+IMUx3+GPS'
            if imu_temp_enabled:
                temp = (((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) / 333.87) + 21.0
            else:
                temp = ((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) * 0.0078125

            if (temp < 0):
                temp = temp + 100.0
                inWater = False
            else:
                inWater = True

            Ax = float((decoded[i + 5] << 8) + decoded[i + 6])
            Ay = float((decoded[i + 7] << 8) + decoded[i + 8])
            Az = float((decoded[i + 9] << 8) + decoded[i + 10])

            if Ax >= 0x8000:
                Ax -= 0x10000
            if Ay >= 0x8000:
                Ay -= 0x10000
            if Az >= 0x8000:
                Az -= 0x10000

            Ax /= float(0x8000 / ACCELEROMETER_MAX)
            Ay /= float(0x8000 / ACCELEROMETER_MAX)
            Az /= float(0x8000 / ACCELEROMETER_MAX)

            Gx = float((decoded[i + 11] << 8) + decoded[i + 12])
            Gy = float((decoded[i + 13] << 8) + decoded[i + 14])
            Gz = float((decoded[i + 15] << 8) + decoded[i + 16])

            if Gx >= 0x8000:
                Gx -= 0x10000
            if Gy >= 0x8000:
                Gy -= 0x10000
            if Gz >= 0x8000:
                Gz -= 0x10000

            Gx /= float(0x8000 / GYROSCOPE_MAX)
            Gy /= float(0x8000 / GYROSCOPE_MAX)
            Gz /= float(0x8000 / GYROSCOPE_MAX)

            Mx = float((decoded[i + 18] << 8) + decoded[i + 17])
            My = float((decoded[i + 20] << 8) + decoded[i + 19])
            Mz = float((decoded[i + 22] << 8) + decoded[i + 21])

            if Mx >= 0x8000:
                Mx -= 0x10000
            if My >= 0x8000:
                My -= 0x10000
            if Mz >= 0x8000:
                Mz -= 0x10000

            Mx *= MAG_CONVERSION
            My *= MAG_CONVERSION
            Mz *= MAG_CONVERSION

            if CREATE_IMU_LOG:
                csvfileWriter.writerow(
                    [str(time),
                     Ax, Ay, Az, vector_magnitude(Ax, Ay, Az),
                     Gx, Gy, Gz, vector_magnitude(Gx, Gy, Gz),
                     Mx, My, Mz, vector_magnitude(Mx, My, Mz), ])

            lat = ((-256*256*256*128 * (decoded[i+23] >> 7)) + ((decoded[i+23] & 0x7F) << 24) + ((decoded[i+24]) << 16) + ((decoded[i+25]) << 8) + ((decoded[i+26])))/1000000.0
            lng = ((-256*256*256*128 * (decoded[i+27] >> 7)) + ((decoded[i+27] & 0x7F) << 24) + ((decoded[i+28]) << 16) + ((decoded[i+29]) << 8) + ((decoded[i+30])))/1000000.0
            print("type = " + str(type_name))
            print("time = " + str(time) + " sec")
            print("temp = " + str(temp) + " C")
            print("In Water? = " + str(inWater))
            print("Ax = " + str(Ax) + " g")
            print("Ay = " + str(Ay) + " g")
            print("Az = " + str(Az) + " g")
            print("Gx = " + str(Gx) + " dps")
            print("Gy = " + str(Gy) + " dps")
            print("Gz = " + str(Gz) + " dps")
            print("Mx = " + str(Mx) + " uT")
            print("My = " + str(My) + " uT")
            print("Mz = " + str(Mz) + " uT")
            print("lat = " + str(lat) + " deg")
            print("lng = " + str(lng) + " deg")
            print("")
            i = i + 3 + 2 + 3*(2*3) + 2*4

csvfile.close()

