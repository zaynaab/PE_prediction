#!/usr/local/bin/python

docstring = """
DESCRIPTION
    Analyzes model results

USAGE:

"""

import glob
import re
import pandas as pd
import numpy as np
import matplotlib
import datetime

matplotlib.use('TkAgg')
import warnings
import matplotlib.pyplot as plt
import itertools
import numpy as np
import seaborn as sns
import statsmodels.api as sm
from statsmodels.tsa.stattools import acf
from statsmodels.tsa.stattools import pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller


def returnNas():
    return pd.Series([Nan, Nan, Nan, Nan, Nan, Nan, Nan, Nan, Nan, Nan, Nan, Nan, Nan, Nan, Nan, Nan],
                     index=columns)


def accuracyAtDay(trueNegatives, truePositives, dfindex, age):
    return (trueNegatives.shape[0] + truePositives.loc[truePositives['predictGestAge'] < age].shape[0]) / dfindex


def preDeliveryAccuracyAtDay(trueNegatives, truePositives, dfindex, age):
    return (trueNegatives.shape[0] + truePositives.loc[
        truePositives['predictGestAge'] < (truePositives['birthAge'] - age)].shape[0]) / dfindex


def preAdmissionAccuracyAtDay(trueNegatives, truePositives, falseNegatives, dfindex, age):
    newTrue = truePositives.loc[
        truePositives['predictGestAge'] < (truePositives[
                                               'micAdmissionAge'] - age)].shape[0]
    # return newTrue / (truePositives.shape[0]+falseNegatives.shape[0])
    return newTrue / (truePositives.shape[0])


def sensitivityAtDay(truePositives, falseNegatives, age):
    return ((truePositives.loc[truePositives['predictGestAge'] < age].shape[0])/(truePositives.loc[truePositives['predictGestAge'] < age].shape[0]+falseNegatives.shape[0]))

def specificityAtDay(trueNegatives, falsePositives, age):
    return trueNegatives.shape[0] / (falsePositives.loc[
                                         falsePositives['predictGestAge'] < (falsePositives['birthAge'] - age)].shape[
                                         0] + trueNegatives.shape[0])

def summarize(df):
    desc = pd.read_csv("data internship/Samenvatting_notwins.csv", sep=',', header=0, encoding="ISO-8859-1",
                       index_col='Premom')

    truePositives = df.loc[(df['predictHypertension'] == True) & (df['predictCorrect'] == True)]
    falsePositives = df.loc[(df['predictHypertension'] == True) & (df['predictCorrect'] == False)]
    trueNegatives = df.loc[(df['predictHypertension'] == False) & (df['predictCorrect'] == True)]
    falseNegatives = df.loc[(df['predictHypertension'] == False) & (df['predictCorrect'] == False)]
    acceptedTM = df.loc[df['admittedDueToTM'] == True]

    accuracyAtEvent = (trueNegatives.shape[0] + truePositives.loc[
        (truePositives['predictGestAge'] < truePositives['birthAge']) |
        (truePositives['predictGestAge'] < truePositives['micAdmissionAge'])].shape[0]) / df.shape[0]
    try:
        sensitivity = truePositives.shape[0] / (truePositives.shape[0] + falseNegatives.shape[0])
        specificity = trueNegatives.shape[0] / (trueNegatives.shape[0] + falsePositives.shape[0])
    except:
        returnNas()

    # Start saving values for output
    output = [truePositives.shape[0], falsePositives.shape[0], trueNegatives.shape[0], falseNegatives.shape[0],
              accuracyAtEvent, sensitivity, specificity]

    columns = ['truePositives', 'falsePositives', 'trueNegatives', 'falseNegatives', 'accuracyAtEvent', 'sensitivity',
               'specificity']
    for i in range(100, 290, 1):
        columns.append('accuracyAtGestAge' + str(i))
        output.append(accuracyAtDay(trueNegatives, truePositives, len(df.index), i))
        columns.append('sensitivityAtGestAge' + str(i))
        output.append(sensitivityAtDay(truePositives, falseNegatives, i))

    for i in range(0, 57, 7):
        columns.append('preDeliveryAccuracy' + str(i))
        columns.append('preAdmissionAccuracy' + str(i))
        # columns.append('sensititivityAtDay' +str(i))
        columns.append('specificityAtDay' + str(i))
        output.append(preDeliveryAccuracyAtDay(trueNegatives, truePositives,
                                               len(df.index), i))
        output.append(preAdmissionAccuracyAtDay(trueNegatives, acceptedTM, falseNegatives,
                                                len(df.index), i))
        # output.append(sensitivityAtDay(truePositives, falseNegatives, i))
        output.append(specificityAtDay(trueNegatives, falsePositives, i))

    try:
        outputFrame = pd.DataFrame(columns=columns)
        outputFrame = outputFrame.append(pd.Series(output, index=columns), ignore_index=True)
    except:
        outputFrame = pd.DataFrame(data=output, columns=columns)
    return outputFrame
