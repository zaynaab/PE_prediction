#!/usr/local/bin/python

docstring= """
DESCRIPTION
    1. groups cleaned blood pressure .csv by username
    2. match with summary .csv to get other values (starting with "admission MIC because of TM" and "date admission mic"
    3. 

USAGE:

"""

import glob
import re
import pandas as pd
import numpy as np
import matplotlib
import datetime
import os
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

#function to check if directory exists for each user
def ensure_dir(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

#function for generating dummy observation by copying
def dummyObservation(user, userName, gestAge, dia, sys, morning, day):
    new = pd.DataFrame(user, columns=data.columns)
    # propogate new values:
    new.loc[-1, 'username'] = userName
    new.loc[-1, 'gestational_age'] = gestAge
    new.loc[-1, 'diastolic'] = dia
    new.loc[-1, 'systolic'] = sys
    new.loc[-1, 'morning'] = morning
    # indicate fake observation:
    new.loc[-1, 'dummy_value'] = True
    new.loc[-1, 'measured_at'] = day
    return(new)


datadata = pd.read_csv("cleanedBloodPressure.csv", sep=',', header=0, parse_dates=['measured_at'], dayfirst=True)
datadata = datadata.ix[:,1:]
descOrig = pd.read_csv("data internship/Samenvatting_notwins.csv", sep=',', header=0, encoding = "ISO-8859-1", index_col='Premom')
desc = descOrig



relevantValues = ['Admission MIC because of TM?','Date admission MIC']
# value to filter out short series

data = pd.DataFrame(datadata)
data.sort_values(['username','measured_at'], inplace=True, ascending=True)

oldName = ''
# add date/time column with time since experiment began

# standardize date time of 'Date admission MIC '

# generate boolean variable for discriminating whether or not a value came before MIC admission event for further analysis

real = 0
afternoonMinusMorning = 0
interpolCutoff = 28

for index, row in data.iterrows():
    if row['username'] != oldName:
        oldName = row['username']
        oldDatetimetime = row['measured_at']
    newDate = row['measured_at']-oldDatetimetime
    # fix username:
    data.loc[index, 'measured_since_first'] = newDate
    data.loc[index, 'measured_since_first'] = newDate

    try:
        # am or pm
        if row['measured_at'].hour > 12:
            data.loc[index, 'morning'] = False
            afternoonMinusMorning = afternoonMinusMorning + 1
        else:
            data.loc[index, 'morning'] = True
            afternoonMinusMorning = afternoonMinusMorning - 1


        # parse ga inclusion + gestational time

        inclusionDate = pd.to_datetime(desc.ix[row['username']]['Inclusiedate'])
        inclusionGA = str(desc.ix[row['username']]['GA inclusion'])
        weeksDiff = int(inclusionGA.split(" ")[0][:-1])
        daysDiff = int(inclusionGA.split(" ")[1][0])
        sinceFirst = newDate.days
        #parsing = 'weeks='+str(weeksDiff) + ', days='+str(daysDiff)
        #print(parsing)
        #deltaDays = datetime.timedelta(parsing)
        if (desc.ix[row['username']]['# MIC admissions since telemonitoring']) > 0:
            data.loc[index, 'admitted'] = int(1)
        else:
            data.loc[index, 'admitted'] = int(0)
        data.loc[index, 'gestational_age'] = int(datetime.timedelta(**{'days': weeksDiff*7+daysDiff+sinceFirst}).days)

        if (pd.to_datetime(row['measured_at'])) > (pd.to_datetime(desc.ix[row['username']]['Date admission MIC '])):

            data.loc[index, 'measured_after_admission'] = int(1)

        else:
            data.loc[index, 'measured_after_admission'] = int(0)
        data.loc[index, 'Date admission MIC '] = pd.to_datetime(desc.ix[row['username']]['Date admission MIC '])
    except:
        data.loc[index, 'measured_after_admission'] = ''
        continue

diffs = []
oldName = ''
data.sort_values( ["username","measured_at"], ascending=[True,True] )
data['dummy_value'] = False

data['diastolic'] = data.groupby(['username','morning','gestational_age'])['diastolic'].transform('max')
data['systolic'] = data.groupby(['username','morning','gestational_age'])['systolic'].transform('max')
data.drop_duplicates(['username','morning','gestational_age'], inplace=True)


# problems: inconsistent time step, unmatched datapoints
matched = 0
unmatched = -1
daySkip = 0
extra = pd.DataFrame.from_items([(name, pd.Series(data=None, dtype=series.dtype)) for name, series in data.iteritems()])

for index, row in data.iterrows():
    #initialize new user, check if am/pm count are equal.
    if row['username'] != oldName:
        # save old
        oldName = row['username']
        oldDatetime = row['measured_at']
        # reset day skip for user
        daySkip = 0
        try:
            # dummy variable if date changes without matched am/pm values
            if matched != 0:
                unmatched = unmatched + 1

        except:
            print('fail')
            continue
    if row['measured_at'].date != oldDatetime.date:

        try:
            # dummy variable if date changes without matched am/pm values
            if matched != 0:
                unmatched = unmatched + 1

        except:
            continue
        matched = 0
        # check to see if days are consecutive, generate dummy variables for if they are not
        diff = row['measured_at'] - oldDatetime
        if diff.days > 1:
            if diff.days < interpolCutoff:
                interpolSYS = interp1d(data.loc[data['username'] == row['username']]['gestational_age'],data.loc[data['username'] == row['username']]['systolic'])
                interpolDIA = interp1d(data.loc[data['username'] == row['username']]['gestational_age'],
                                       data.loc[data['username'] == row['username']]['diastolic'])
                inter = 1
                gestAge = row['gestational_age']
                day = row['measured_at']
                while int(inter)<int(diff.days):
                    try:
                        # generate new data for each day
                        userName = row['username']
                        gestAge = gestAge - 1
                        newSYS = interpolSYS(gestAge)
                        newDIA = interpolDIA(gestAge)
                        inter = inter + 1
                        day = day-datetime.timedelta(days=1)
                        #generate morning and afternoon values
                        newEntry = dummyObservation(row, userName, gestAge, newDIA, newSYS, True, day)
                        extra = extra.append(newEntry, ignore_index=True)
                        newEntry = dummyObservation(row, userName, gestAge, newDIA, newSYS, False, day)
                        extra = extra.append(newEntry, ignore_index=True)
                        print('WOOOOOO')
                        print(row['username'])
                    except:
                        print('fail')
                        continue
            else:
                daySkip = 1

        oldDatetime = row['measured_at']

    else:
        if row['measured_at'].hour > 12:
            matched = matched + 1
        else:
            matched = matched - 1
    data.loc[index, 'after_skipped_days'] = daySkip


colList = list(data.columns.values)
extra = extra.ix[:,colList]
data = data.append(extra, ignore_index=True)
# check for multiple values for AM or PM and consolidate

data1 = data[data.morning == True]
data1 = data1[data1.after_skipped_days != 1]
output = data1

output.to_csv("user/bloodPressureModeledAM.csv")

data2 = data[data.morning == False]
data2 = data2[data2.after_skipped_days != 1]
output = data2

output.to_csv("user/bloodPressureModeledPM.csv")

# generate folders, data for morning by username
for label, df in data1.groupby('username'):
    try:
        userDir = "user/" + label
        ensure_dir(userDir)
        df.to_csv(userDir+"/BP_AM2.csv")
    except:
        print('fail')
        continue
# generate folders, data for afternoon by username
for label, df in data1.groupby('username'):
    try:
        userDir = "user/" + label
        ensure_dir(userDir)
        df.to_csv(userDir+"/BP_PM2.csv")
    except:
        print('fail')
        continue
