# Version Notes
# V3 adds 16bit IMU data conversion, removes imu temp option

import base64
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

from sklearn import linear_model

plt.close('all') 

#%% Data Types
TEMP_DATA_TYPE = 1
IMU_DATA_TYPE = 2
GPS_DATA_TYPE = 3
TEMP_IMU_DATA_TYPE = 4
TEMP_GPS_DATA_TYPE = 5
TEMP_IMU_GPS_DATA_TYPE = 6
BATT_DATA_TYPE = 7
TEMP_EPOCH_DATA_TYPE = 8
TEXT_DATA_TYPE = 15

TEMP_DATA_TYPE_PAYLOAD_SIZE = 2
IMU_DATA_TYPE_PAYLOAD_SIZE = 6
GPS_DATA_TYPE_PAYLOAD_SIZE = 8
TEMP_IMU_DATA_TYPE_PAYLOAD_SIZE = 8
TEMP_GPS_DATA_TYPE_PAYLOAD_SIZE = 10
TEMP_IMU_GPS_DATA_TYPE_PAYLOAD_SIZE = 16
BATT_DATA_TYPE_PAYLOAD_SIZE = 2
TEMP_EPOCH_DATA_TYPE_PAYLOAD_SIZE = 6

#acceleration full scale [g]
A_RES = 2.0

#%% Data upload
# Raw Smartfin ascii85 characters, just one long string saved as CSV
filename_smartfin = '20190314_Z7CalTest2_SF'
fileloc_smartfin = os.path.join('Data', filename_smartfin+'.csv')
data_raw_smartfin = pd.read_csv(fileloc_smartfin, header = None)

# Raw CTD data with extra whitespace (deal with LabVIEW software, preferably)
filename_CTD = '20190314_Z7CalTest2_CTD'
fileloc_CTD = os.path.join('Data', filename_CTD+'.txt')
df_ctd_badspacing = pd.read_csv(fileloc_CTD, delimiter = '\t', skiprows = 2, header = None, parse_dates = [[0, 1]])

#%% Convert decoded bytes to DataFrame
data_to_decode = data_raw_smartfin.iat[0, 0]
decoded = base64.b85decode(data_to_decode)

def decoded_to_df(df, decoded):
    
    i = 0
    
    # rest vars
    type_name = np.nan
    time = np.nan
    temp = np.nan
    epoch = np.nan
    wet = np.nan
    ax = np.nan
    ay = np.nan
    az = np.nan
    lat = np.nan
    lon = np.nan
    text = np.nan
    batt_mv = np.nan
    
    while(i < (len(decoded))):
        type = (decoded[i]>>4)

        # deal with padding if it exists
        if (type == 0):
            type_name = 'Padding'
            i = i + 1
            # print("type = " + str(type_name))
            # print()
            continue

        # grab time (wait until after dealing with padding)
        time = (((decoded[i] & 0x0F) << 16) + (decoded[i+1] << 8) + decoded[i+2])/10.0

        # decode data type

        if (type == TEMP_DATA_TYPE):
            type_name = 'TEMP'
            temp = ((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) * 0.0078125

            if (temp < 0):
                temp = temp + 100.0
                inWater = False
            else:
                inWater = True
            # print("type = " + str(type_name))
            # print("time = " + str(time) + " sec")
            # print("temp = " + str(temp) + " C")
            # print("In Water? = " + str(inWater))
            # print("")
            i = i + 3 + TEMP_DATA_TYPE_PAYLOAD_SIZE

        elif (type == IMU_DATA_TYPE):
            type_name = 'IMU'
            Ax = ((-32768 * (decoded[i+3] >> 7)) +  (256 * (decoded[i+3] & 0x7F)) + (decoded[i+4])) * A_RES/32768
            Ay = ((-32768 * (decoded[i+5] >> 7)) +  (256 * (decoded[i+5] & 0x7F)) + (decoded[i+6])) * A_RES/32768
            Az = ((-32768 * (decoded[i+7] >> 7)) +  (256 * (decoded[i+7] & 0x7F)) + (decoded[i+8])) * A_RES/32768

            # print("type = " + str(type_name))
            # print("time = " + str(time) + " sec")
            # print("Ax = " + str(Ax) + " g")
            # print("Ay = " + str(Ay) + " g")
            # print("Az = " + str(Az) + " g")
            # print("")
            i = i + 3 + IMU_DATA_TYPE_PAYLOAD_SIZE

        elif (type == TEMP_IMU_DATA_TYPE):
            type_name = 'TEMP+IMU'
            temp = ((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) * 0.0078125

            if (temp < 0):
                temp = temp + 100.0
                inWater = False
            else:
                inWater = True

            Ax = ((-32768 * (decoded[i+5] >> 7)) +  (256 * (decoded[i+5] & 0x7F)) + (decoded[i+6])) * A_RES/32768
            Ay = ((-32768 * (decoded[i+7] >> 7)) +  (256 * (decoded[i+7] & 0x7F)) + (decoded[i+8])) * A_RES/32768
            Az = ((-32768 * (decoded[i+9] >> 7)) +  (256 * (decoded[i+9] & 0x7F)) + (decoded[i+10])) * A_RES/32768

            # print("type = " + str(type_name))
            # print("time = " + str(time) + " sec")
            # print("temp = " + str(temp) + " C")
            # print("In Water? = " + str(inWater))
            # print("Ax = " + str(Ax) + " g")
            # print("Ay = " + str(Ay) + " g")
            # print("Az = " + str(Az) + " g")
            # print("")
            i = i + 3 + TEMP_IMU_DATA_TYPE_PAYLOAD_SIZE

        elif (type == TEMP_IMU_GPS_DATA_TYPE):
            type_name = 'TEMP+IMU+GPS'
            temp = ((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) * 0.0078125

            if (temp < 0):
                temp = temp + 100.0
                inWater = False
            else:
                inWater = True

            Ax = ((-32768 * (decoded[i+5] >> 7)) +  (256 * (decoded[i+5] & 0x7F)) + (decoded[i+6])) * A_RES/32768
            Ay = ((-32768 * (decoded[i+7] >> 7)) +  (256 * (decoded[i+7] & 0x7F)) + (decoded[i+8])) * A_RES/32768
            Az = ((-32768 * (decoded[i+9] >> 7)) +  (256 * (decoded[i+9] & 0x7F)) + (decoded[i+10])) * A_RES/32768

            lat = ((-256*256*256*128 * (decoded[i+11] >> 7)) + ((decoded[i+11] & 0x7F) << 24) + ((decoded[i+12]) << 16) + ((decoded[i+13]) << 8) + ((decoded[i+14])))/1000000.0
            lng = ((-256*256*256*128 * (decoded[i+12] >> 15)) + ((decoded[i+16] & 0x7F) << 24) + ((decoded[i+17]) << 16) + ((decoded[i+18]) << 8) + ((decoded[i+19])))/1000000.0
            # print("type = " + str(type_name))
            # print("time = " + str(time) + " sec")
            # print("temp = " + str(temp) + " C")
            # print("In Water? = " + str(inWater))
            # print("Ax = " + str(Ax) + " g")
            # print("Ay = " + str(Ay) + " g")
            # print("Az = " + str(Az) + " g")
            # print("lat = " + str(lat) + " deg")
            # print("lng = " + str(lng) + " deg")
            # print("")
            i = i + 3 + TEMP_IMU_GPS_DATA_TYPE_PAYLOAD_SIZE

        elif (type == TEXT_DATA_TYPE):
            type_name = 'TEXT'
            # get text string length
            temp = decoded[i+3]

            # print("type = " + str(type_name))
            # print("time = " + str(time) + " sec")
            # print("text = " + str(decoded[i+4: i+4+temp]))
            print("")
            i = i + 4 + temp

        elif (type == BATT_DATA_TYPE):
            type_name = 'BATT INFO'
            # get text string length
            batt_mv = (decoded[i+3] << 8) + decoded[i+4]

            # print("type = " + str(type_name))
            # print("time = " + str(time) + " sec")
            # print("batt = " + str(batt_mv / 1000.0) + " V")
            # print("")
            i = i + 3 + BATT_DATA_TYPE_PAYLOAD_SIZE

        elif (type == TEMP_EPOCH_DATA_TYPE):
            type_name = 'TEMP+EPOCH'
            temp = ((-32768 * (decoded[i+3] >> 7)) + ((decoded[i+3] & 0x7F) << 8) + decoded[i+4]) * 0.0078125

            if (temp < 0):
                temp = temp + 100.0
                inWater = False
            else:
                inWater = True
            epoch = ((256*256*256) * (decoded[i+5] & 0xFF)) + ((256*256) * (decoded[i+6] & 0xFF)) + ((256) * (decoded[i+7] & 0xFF)) + (decoded[i+8] & 0xFF)

            
            # print("type = " + str(type_name))
            # print("time = " + str(time) + " sec")
            # print("temp = " + str(temp) + " C")
            # print("In Water? = " + str(inWater))
            # print("EPOCH time = " + str(epoch))
            # print("")
            i = i + 3 + TEMP_EPOCH_DATA_TYPE_PAYLOAD_SIZE


        # append row to dataframe
        data = np.array([type_name, time, temp, wet, ax, ay, az, lat, lon, text, batt_mv])
        df = df.append({'type_name': type_name,
                        'time': time,
                        'epoch': epoch,
                        'temp': temp,
                        'wet': wet,
                        'ax':ax,
                        'ay':ay,
                        'az':az,
                        'lat': lat,
                        'lon': lon,
                        'text': text,
                        'batt_v': batt_mv/1000
                        }, ignore_index=True)
    return df

#%% Create DF, decode data, add to DF
# create df
columns = ['type_name', 'time', 'epoch', 'temp', 'wet', 'ax', 'ay', 'az', 'lat', 'lon', 'text', 'batt_v']
df_sf = pd.DataFrame(columns=columns) # initialize
df_sf = decoded_to_df(df_sf, decoded)

# Convert epoch time to datetime 
df_sf['DateTimeUTC'] = pd.to_datetime(df_sf['epoch'], unit = 's', utc = True)

#%% Read in Sea-Bird CTD data
df_ctd = (df_ctd_badspacing.iloc[0::2, :]).copy(deep = True) # lots of blank lines, every other
del df_ctd_badspacing
df_ctd.reset_index(inplace = True, drop = True) # it keeps the 0::2 indexes; reset to 0::1
df_ctd.columns = ['DateTime', 'SetTempC', 'TempCTD_C', 'CondCTD_mScm', 'SalCTD'] # name columns
df_ctd['DateTimePT'] = pd.to_datetime(df_ctd['DateTime'], utc = False) # parse_dates doesn't properly convert timestamp
df_ctd.drop(columns = 'DateTime', inplace = True) # get rid of old, bad timestamp and keep the new one with type datetime64
df_ctd.set_index(df_ctd['DateTimePT'], drop = True, inplace = True) # can only convert timestamp on index for some stupid pandas reason
df_ctd['DateTimeUTC'] = df_ctd.index.tz_localize(tz = 'US/Pacific').tz_convert('UTC')

#%% Plot
fig, axs = plt.subplots();
plt.plot(df_ctd['DateTimeUTC'], df_ctd['TempCTD_C'], 'k.')
plt.plot(df_sf['DateTimeUTC'], df_sf['temp'], 'bo')

## Formatting
# Rotate date labels automatically
fig.autofmt_xdate()
axs.set_ylabel('Temperature (C)')

#%% Select time windows of stable temperature
win1_start = pd.to_datetime('2019-03-15 03:03:35', utc = True)
win2_start = pd.to_datetime('2019-03-15 06:03:35', utc = True)
win3_start = pd.to_datetime('2019-03-15 09:03:35', utc = True)
win4_start = pd.to_datetime('2019-03-15 12:03:35', utc = True)

win_start = [win1_start, win2_start, win3_start, win4_start]

# Loop through and plot start and end times
for i in range(len(win_start)):
    win_start_i = win_start[i]
    win_end_i = win_start_i+pd.to_timedelta(60, 's')
    plt.plot([win_start_i, win_start_i], [0, 25])
    plt.plot([win_end_i, win_end_i], [0, 25])


#%% Extract CTD and Smartfin temps in those windows
temp_ctd = []
temp_sf_precal = []
square_error_sum = 0
for i in range(len(win_start)):
    win_start_i = win_start[i]
    win_end_i = win_start_i+pd.to_timedelta(60, 's')
    
    good_times_ctd_i = (df_ctd['DateTimeUTC'] > win_start_i) & (df_ctd['DateTimeUTC'] < win_end_i)
    good_temps_ctd_i = df_ctd['TempCTD_C'][good_times_ctd_i] # array within good times
    temp_ctd_i = np.nanmean(good_temps_ctd_i)
    temp_ctd.append(temp_ctd_i)
    
    good_times_sf_i = (df_sf['DateTimeUTC'] > win_start_i) & (df_sf['DateTimeUTC'] < win_end_i)
    good_temps_sf_i = df_sf['temp'][good_times_sf_i] # array within good times
    temp_sf_precal_i = np.nanmean(good_temps_sf_i)
    temp_sf_precal.append(temp_sf_precal_i)
    
    square_error_sum += (temp_sf_precal_i-temp_ctd_i)**2
    
RMSE = (square_error_sum/len(temp_ctd))**0.5
print("RMSE for no correction = {}".format(RMSE))
    
#%% Plot average values
fig, axs = plt.subplots();
plt.plot(temp_sf_precal, temp_ctd, '.')

# For 1:1 line
temp_max = np.nanmax(temp_ctd)
temp_min = np.nanmin(temp_ctd)

plt.plot([temp_min, temp_max], [temp_min, temp_max], 'r--')
axs.set_xlabel('Temp Smartfin (C)')
axs.set_ylabel('Temp CTD (C)')

#%% Linear regression
reg = linear_model.LinearRegression()
X = np.array(temp_sf_precal).reshape(-1, 1) # reg.fit needs a 2-D array
y = np.array(temp_ctd).reshape(-1, 1) # reg.fit needs a 2-D array
reg.fit(X = X, y = y)

# print(reg.coef_, reg.intercept_)

#%% Plot all time-series data again after applying linreg coeffs to Smartfin
df_sf['temp_cal'] = df_sf['temp']*reg.coef_[0]+reg.intercept_ # apply linreg coeffs

fig, axs = plt.subplots();
plt.plot(df_ctd['DateTimeUTC'], df_ctd['TempCTD_C'], 'k.')
plt.plot(df_sf['DateTimeUTC'], df_sf['temp_cal'], 'bo')

## Formatting
# Rotate date labels automatically
fig.autofmt_xdate()
axs.set_ylabel('Temperature (C)')

#%% Calculate error
temp_sf_postcal = []
square_error_sum = 0
for i in range(len(win_start)):
    win_start_i = win_start[i]
    win_end_i = win_start_i+pd.to_timedelta(60, 's')
    
    good_times_sf_i = (df_sf['DateTimeUTC'] > win_start_i) & (df_sf['DateTimeUTC'] < win_end_i)
    good_temps_postcal_sf_i = df_sf['temp_cal'][good_times_sf_i] # array within good times
    temp_sf_postcal_i = np.nanmean(good_temps_postcal_sf_i)
    temp_sf_postcal.append(temp_sf_postcal_i)
    
    temp_ctd_i = temp_ctd[i]
    
    square_error_sum += (temp_sf_postcal_i-temp_ctd_i)**2
    
RMSE = (square_error_sum/len(temp_ctd))**0.5
print("RMSE for slope and intercept = {}".format(RMSE))

#%% Intercept only correction
offset = np.nanmean(temp_ctd)-np.nanmean(temp_sf_precal)

#%% Plot all time-series data again after applying linreg coeffs to Smartfin
df_sf['temp_cal'] = df_sf['temp']+offset # apply linreg coeffs

fig, axs = plt.subplots();
plt.plot(df_ctd['DateTimeUTC'], df_ctd['TempCTD_C'], 'k.', label = 'CTD')
plt.plot(df_sf['DateTimeUTC'], df_sf['temp'], 'ro', label = 'pre cal')
plt.plot(df_sf['DateTimeUTC'], df_sf['temp_cal'], 'bo', label = 'post cal')

plt.legend()

# Loop through and plot start and end times
for i in range(len(win_start)):
    win_start_i = win_start[i]
    win_end_i = win_start_i+pd.to_timedelta(60, 's')
    plt.plot([win_start_i, win_start_i], [0, 25])
    plt.plot([win_end_i, win_end_i], [0, 25])
    
## Formatting
# Rotate date labels automatically
fig.autofmt_xdate()
axs.set_ylabel('Temperature (C)')
plt.savefig(filename_smartfin+'.png')
#%% Calculate error
temp_sf_postcal = []
square_error_sum = 0
for i in range(len(win_start)):
    win_start_i = win_start[i]
    win_end_i = win_start_i+pd.to_timedelta(60, 's')
    
    good_times_sf_i = (df_sf['DateTimeUTC'] > win_start_i) & (df_sf['DateTimeUTC'] < win_end_i)
    good_temps_postcal_sf_i = df_sf['temp_cal'][good_times_sf_i] # array within good times
    temp_sf_postcal_i = np.nanmean(good_temps_postcal_sf_i)
    temp_sf_postcal.append(temp_sf_postcal_i)
    
    temp_ctd_i = temp_ctd[i]
    
    square_error_sum += (temp_sf_postcal_i-temp_ctd_i)**2
    
RMSE = (square_error_sum/len(temp_ctd))**0.5
print("RMSE for offset only = {}".format(RMSE))