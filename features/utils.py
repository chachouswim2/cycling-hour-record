import pandas as pd
from pathlib import Path
from os import listdir
from os.path import isfile, join
from benedict import benedict as bdict
from ipyleaflet import Map, Polyline
from datetime import datetime, timedelta, time
import dateutil.parser as dparser
import requests
import pickle
import gzip
import shutil
from sklearn import preprocessing
from matplotlib.axes._axes import _log as matplotlib_axes_logger
matplotlib_axes_logger.setLevel('ERROR')

# Mutual functions across notebooks
filepath = "data/"
fileOutputPath = filepath + "output/"
activityPath = filepath + "activities/"
activitycsvPath = filepath + "activities_csv/"
activityOutputPath = fileOutputPath + "activities/"

def preprocess_date_column(data):
    # Extract the date and time in two columns
    data[['Date', 'Time']] = data['Date de l\'activité'].str.split('à', expand=True)
    
    # Replace the month abbreviations with numbers
    data['Date'] = data['Date'].str.replace('janv.', '01', regex=True)
    data['Date'] = data['Date'].str.replace('févr.', '02', regex=True)
    data['Date'] = data['Date'].str.replace('mars', '03', regex=True)
    data['Date'] = data['Date'].str.replace('avr.', '04', regex=True)
    data['Date'] = data['Date'].str.replace('mai', '05', regex=True)
    data['Date'] = data['Date'].str.replace('juin', '06', regex=True)
    data['Date'] = data['Date'].str.replace('juil.', '07', regex=True)
    data['Date'] = data['Date'].str.replace('août', '08', regex=True)
    data['Date'] = data['Date'].str.replace('sept.', '09', regex=True)
    data['Date'] = data['Date'].str.replace('oct.', '10', regex=True)
    data['Date'] = data['Date'].str.replace('nov.', '11', regex=True)
    data['Date'] = data['Date'].str.replace('déc.', '12', regex=True)

    # Convert date and time to datetime and time format respectively
    data['Date'] = data['Date'].apply(lambda x: dparser.parse(x, fuzzy=True, dayfirst=True))
    data['Time'] = pd.to_datetime(data['Time'], format=' %H:%M:%S').dt.time
    
    return data

def loadData():
    df = pd.read_csv(filepath + 'activities.csv')
    data = df[df.columns[[0, 1, 2, 3, 4, 5, 8, 11, 12, 13, 14, 16, 17, 18, 19,
                          20, 21, 22, 23, 24, 25, 28, 29, 31, 33, 34, 36, 46, 47,
                          59, 61, 72, 74]]]

    #Convert distance to km
    data = data.rename(columns={"Distance.1": "Distance"})
    data["Distance"] = round(data["Distance"]/1000, 2)

    # Convert "Vitesse max." and "Vitesse moyenne" from m/s to km/h
    data["Vitesse max."] = round(data["Vitesse max."] * 3.6, 2)
    data["Vitesse moyenne"] = round(data["Vitesse moyenne"] * 3.6, 2)

    #convert date time
    data = preprocess_date_column(data)
    data['Week'] = data['Date'].dt.isocalendar().week
    data['Month'] = data['Date'].dt.month

    #convert time to minutes
    data['Temps écoulé'] = round(data['Temps écoulé'] / 60, 2)
    data['Durée de déplacement'] = round(data['Durée de déplacement'] / 60, 2)

    rideTypes = ['Vélo', 'Vélo virtuel']
    rideData = data[data["Type d'activité"].isin(rideTypes)]

    return rideData