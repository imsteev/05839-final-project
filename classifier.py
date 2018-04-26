import numpy as np
import pandas as pd
from datetime import date, datetime
import sklearn

YEAR = 1992
COLS_NEEDED = [
    "FIRE_YEAR",
    "DISCOVERY_DATE",
    "DISCOVERY_DOY",
    "DISCOVERY_TIME",
    "STAT_CAUSE_CODE",
    "STAT_CAUSE_DESCR",
    "CONT_DATE",
    "CONT_DOY",
    "CONT_TIME",
    "FIRE_SIZE",
    "FIRE_SIZE_CLASS",
    "LATITUDE",
    "LONGITUDE",
    "STATE",
    "COUNTY"
]

with open('./wildfires_%d.csv' % YEAR) as csvfile:
    df = pd.read_csv(csvfile)
    df = df[COLS_NEEDED]

def get_season(day, Y):
    seasons = [('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
              ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
              ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
              ('autumn', (date(Y,  9, 23),  date(Y, 12, 20))),
              ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))]
    for season in seasons:
        name = season[0]
        start, end = season[1]
        if (start.timetuple().tm_yday <= day <= end.timetuple().tm_yday):
            return name
    return None

def julian_to_datetime(jd_series):
    # https://www.kaggle.com/rtatman/188-million-us-wildfires/discussion/39627#222290
    epoch = pd.to_datetime(0, unit='s').to_julian_date()
    return pd.to_datetime(jd_series - epoch, unit='D')

def difference_in_seconds():
    start_times = df['DISCOVERY_TIME']
    end_times = df['CONT_TIME']
    return pd.to_datetime(end_times) - pd.to_datetime(start_times)

def num_to_time(num_time):
    # num_time is in 24-hour format - so 0 to 2359
    chars = list(str(int(num_time)))
    res = []
    for i in range(len(chars)-1, -1, -1):
      res.append(chars[i])
      if len(res) == 2:
        res.append(":")
    result = ''.join(res[::-1])
    if len(result) == 1: result = "00:0" + result
    if result[0] == ":": result = "00" + result
    return result

df = df.dropna(subset=['CONT_DATE', 'DISCOVERY_DATE', 'CONT_TIME', 'DISCOVERY_TIME'])
df['CONT_TIME'] = df.apply(lambda row: num_to_time(row.CONT_TIME), axis=1)
df['DISCOVERY_TIME'] = df.apply(lambda row: num_to_time(row.DISCOVERY_TIME), axis=1)
df['CONT_DATE'] = df.apply(lambda row: julian_to_datetime(row.CONT_DATE), axis=1)
df['DISCOVERY_DATE'] = df.apply(lambda row: julian_to_datetime(row.DISCOVERY_DATE),axis=1)
df['season'] = df.apply(lambda row: get_season(row.DISCOVERY_DOY,YEAR), axis=1)

full_disc_date = pd.to_datetime(df['DISCOVERY_DATE'].dt.strftime("%Y-%m-%d") + ' ' + df['DISCOVERY_TIME'])
full_cont_date = pd.to_datetime(df['CONT_DATE'].dt.strftime("%Y-%m-%d") + ' ' + df['CONT_TIME'])
df['duration'] = full_cont_date - full_disc_date

# TODO: Create classifier
# - extract features for each row
# - create labels for each row (this should just be getting the fire class size and mapping it to an integer)
# - split data into train + test sets (shuffle data first?)
# - train data using a model (need to look this up)
# - test for accuracy
label_names = [chr(ord('A') + i) for i in range(ord('G') - ord('A') + 1)]
labels = df['FIRE_SIZE_CLASS']

feature_names = ['duration', 'state', 'season', 'cause']