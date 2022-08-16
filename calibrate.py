import sys
import pandas as pd

#this file will let us take in the raw data and then 
#change it to the correct calibrations. 


#run command 'python calibrate.py [file you want to calibrate].csv"
#will make a csv file of the calibrated data (same file name with '_cal-' before it)

#CURRENTLY UNDER CONSTRUCTION!
#WILL CURRENTLY JUST RETURN THE SAME VALUES IT WAS INPUT

file = sys.argv[1]

df = pd.read_csv(file)

#do the changing and transforming here...

df.to_csv("_cal-" + file[1:])

print("Data calibrated.")