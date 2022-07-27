import sys
import pandas as pd

file = sys.argv[1]

df = pd.read_csv(file)

#do all the changing to the dataframe here

df.to_csv("_cal-" + file[1:])

print("Data calibrated.")