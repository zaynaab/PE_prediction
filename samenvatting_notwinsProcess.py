#!/usr/local/bin/python

docstring= """
DESCRIPTION
    Process original csv of heartrate readings:
        1. Make username consistent
        2. Replace duplicate entries with median of values



USAGE:

"""

import glob
import re
import pandas as pd
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import datetime



#function for getting reasons for HR
def getReason(code):
    code = int(code)
    if code == 1:
        return 'bloodCoagulationDisorders'
    elif code == 2:
        return 'PEduringPreviousPregnancy'
    elif code == 3:
        return 'HEELPduringPreviousPregnancy'
    elif code == 4:
        return 'gestationalHypertension'
    elif code == 5:
        return 'highBloodPressureDuringGestation'
    elif code == 6:
        return 'age'
    elif code == 7:
        return 'resultsNICCOMO'
    elif code == 8:
        return 'highBloodPressureDuringPreviousGestation'
    elif code == 9:
        return 'cardialDysfunction'
    elif code == 10:
        return 'other'
    else:
        return 'asdfdfsafsdfdss'





all = pd.read_csv("data internship/Samenvatting_notwins.csv", sep=',', header=0, encoding = "ISO-8859-1")

#all.loc['Date admission MIC '] = pd.to_datetime(all['Date admission MIC '])



# fix column names
all.rename(columns={'Unnamed: 12': 'percentageBPtakenOverExpected', 'Unnamed: 14': 'percentageBPnormal', 'Unnamed: 16': 'percentageBPmedRisk', 'Unnamed: 18': 'percentageBPhighRisk', 'Unnamed: 20': 'percentageBPmissedOverExpected'}, inplace=True)



# fix username and null entries
for index, row in all.iterrows():
    try:
        #print(row['username'])
        idInt = int(''.join(filter(str.isdigit, row['Premom'])))
        if idInt<10:
            id = str('0') + str(idInt)
        else:
            id = str(idInt)
    except:
        id = 'N/A'
    # fix username:
    newname = 'Premom ' + id
    all.loc[index, 'Premom'] = newname
    try:
        admissionDate = row['Date admission MIC ']
        if admissionDate is not None and admissionDate is not 'nan':
            print(admissionDate)
        else:
            all.loc[row, 'Date admission MIC '] = '0'
    except:
        all.loc[row, 'Date admission MIC '] = '0'

    try:
        inclusionGA = str(all.loc[index,'GA inclusion'])
        weeksDiff = int(inclusionGA.split(" ")[0][:-1])
        daysDiff = int(inclusionGA.split(" ")[1][0])
        all.loc[index, 'gestational_age'] = datetime.timedelta(**{'days': weeksDiff * 7 + daysDiff}).days
    except:
        all.loc[index, 'gestational_age'] = 0
        print('fail')

    try:
        deliveryGA = str(all.loc[index,'GA delivery'])
        weeksDiff = int(deliveryGA.split(" ")[0][:-1])
        daysDiff = int(deliveryGA.split(" ")[1][0])
        all.loc[index, 'deliveryGA'] = datetime.timedelta(**{'days': weeksDiff * 7 + daysDiff}).days
    except:
        all.loc[index, 'deliveryGA'] = 0
        print('fail')

# dummy code booleans for risk reasons

    for x in range(1,11):
        all.loc[index, getReason(x)] = 0
    try:
        reasons = str(all.loc[index, 'Reason high risk']).split("+")
        for x in reasons:
            all.loc[index, getReason(x)] = 1

    except:
        print('fail reason classification')





output = all

output.to_csv("cleanedDesc.csv")
