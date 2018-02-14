#!/usr/local/bin/python

docstring = """
DESCRIPTION
    1. Checks if an entry meets requirements for the analysis
    2. Trims gestation ages under cutoff and returns user if dataset length is >0

USAGE:

"""

import csv
import re
import pandas as pd



def returnNas():
    return pd.Series([Nan, Nan, Nan, Nan, Nan],
                     index=resultsColumns)

def appendEntry(user, morning, trimCutoff):
    dir = 'user/' + user + '/'
    data = pd.read_csv(dir + 'BP_' + morning + '_compare2.csv', sep=',', header=0, parse_dates=['measured_at'],
                       dayfirst=False)
    data.sort_values(['measured_at'], inplace=True, ascending=True)
    desc = pd.read_csv("data internship/Samenvatting_notwins.csv", sep=',', header=0, encoding="ISO-8859-1",
                       index_col='Premom')

    desc.ix[:]['Study completed untill delivery/admission MIC?'].fillna(0, inplace=True)

    completion = (bool(desc.ix[user]['Study completed untill delivery/admission MIC?']))

    if completion is not True:
        returnNas()
    if desc.ix[user]["BP's taken"] < 30:
        returnNas()
    if desc.ix[user]['Days participated'] < 30:
        returnNas()

    dateBP = data.filter(items=['gestational_age', 'diastolic', 'systolic'])
    try:
        dateBPcut = dateBP.loc[dateBP['gestational_age'] >= trimCutoff]
    except:
        returnNas()
    if dateBPcut.shape[0]>0:
        return pd.Series([user, morning],
                     index=['user','morning'])
    else:
        returnNas()
