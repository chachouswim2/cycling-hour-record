import pandas as pd
from pathlib import Path
from os import listdir
from os.path import isfile, join
from benedict import benedict as bdict
from ipyleaflet import Map, Polyline
from datetime import datetime, timedelta, time
import dateutil.parser as dparser
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


################################################## PREPROCESS DATA AND LOAD ###############################################
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
                          20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 33, 34, 36, 46, 47,
                          59, 61, 72, 74]]]

    #Rename#Convert distance to km
    data = data.rename(columns={"Fréquence cardiaque maximum.1": "Fréquence cardiaque maximum"})

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

################################################## DATA SUBSET ########################################################

def create_sub_df(df):
     """
    Create a subset of the main activities data frame, dropping the Nan and keeping important columns.

    Args:
        df: activities dataset.

    Returns:
        sub_df: subset data frame
    """
     sub_df = df[["Date", "Time", "Nom du fichier", "Durée de déplacement", "Distance", "Fréquence cardiaque moyenne", 
                  "Fréquence cardiaque maximum", "Vitesse moyenne", "Cadence moyenne", "Puissance moyenne", 
                  "Poids de l'athlète", "Mesure d'effort", "Puissance moyenne pondérée"]]
     
    # Drop the rows where "Fréquence cardiaque moyenne" is NaN
     sub_df = sub_df.dropna(subset=['Fréquence cardiaque moyenne'])

     sub_df['Puissance moyenne pondérée'] = sub_df['Puissance moyenne pondérée'].astype(float)
     
     sub_df = sub_df.reset_index(drop=True)
     
     sub_df['Date'] = pd.to_datetime(sub_df['Date'])

     return sub_df

############################################################### LAURENT SPEED ZONES #############################################################
speed = {
        "Z1": (0, 10),
        "Z2": (10, 15),
        "Z3": (15, 20),
        "Z4": (20, 25),
        "Z5": (25, 27),
        "Z6": (27, 30),
        "Z7": (30, 32),
        "Z8": (32, 34),
        "Z9": (34, 36),
        "Z10": (36, 38),
        "Z11": (38, 40),
        "Z12": (40, 42),
        "Z13": (42, 44),
        "Z14": (44, 47),
        "Z15": (47, 50),
        "Z16": (50, 60),
        "Z17": (60, 75)
}

# create a DataFrame with the zone names, lower and upper bounds
speed_zones_df = pd.DataFrame(speed.items(), columns=['zone', 'bounds'])
speed_zones_df[['lower', 'upper']] = pd.DataFrame(speed_zones_df['bounds'].tolist(), index=speed_zones_df.index)
speed_zones_df = speed_zones_df.drop('bounds', axis=1)


############################################################### LAURENT POWER ZONES #############################################################
power = {
        "Z1": (0, 50),
        "Z2": (50, 100),
        "Z3": (100, 150),
        "Z4": (150, 175),
        "Z5": (175, 200),
        "Z6": (200, 225),
        "Z7": (225, 250),
        "Z8": (250, 300),
        "Z9": (300, 325),
        "Z10": (325, 350),
        "Z11": (350, 375),
        "Z12": (375, 400),
        "Z13": (400, 425),
        "Z14": (425, 450),
        "Z15": (450, 475),
        "Z16": (475, 500),
        "Z17": (500, 600),
        "Z18": (600, 800),
        "Z19": (800, 1500)
}

# create a DataFrame with the zone names, lower and upper bounds
power_zones_df = pd.DataFrame(power.items(), columns=['zone', 'bounds'])
power_zones_df[['lower', 'upper']] = pd.DataFrame(power_zones_df['bounds'].tolist(), index=power_zones_df.index)
power_zones_df = power_zones_df.drop('bounds', axis=1)

############################################################ CADENCE ZONES #######################################################################

cadence = {
        "Z1": (0, 5),
        "Z2": (5, 10),
        "Z3": (10, 15),
        "Z4": (15, 20),
        "Z5": (20, 25),
        "Z6": (25, 30),
        "Z7": (30, 35),
        "Z8": (35, 40),
        "Z9": (40, 45),
        "Z10": (45, 50),
        "Z11": (50, 55),
        "Z12": (55, 60),
        "Z13": (60, 65),
        "Z14": (65, 70),
        "Z15": (70, 75),
        "Z16": (75, 80),
        "Z17": (80, 85),
        "Z18": (85, 90),
        "Z19": (90, 95),
        "Z20": (95, 100),
        "Z21": (100, 105),
        "Z22": (105, 110),
        "Z23": (110, 115),
        "Z24": (115, 125),
        "Z25": (125, 150)
}

# create a DataFrame with the zone names, lower and upper bounds
cadence_zones_df = pd.DataFrame(cadence.items(), columns=['zone', 'bounds'])
cadence_zones_df[['lower', 'upper']] = pd.DataFrame(cadence_zones_df['bounds'].tolist(), index=cadence_zones_df.index)
cadence_zones_df = cadence_zones_df.drop('bounds', axis=1)

################################################# GRADE ZONE ################################

grade = {
        "Z1": (-20, -17),
        "Z2": (-17, -14),
        "Z3": (-14, -12),
        "Z4": (-12, -9),
        "Z5": (-9, -6),
        "Z6": (-6, -3),
        "Z7": (-3, -2),
        "Z8": (-2, -1),
        "Z9": (-1, -0.5),
        "Z10": (-0.5, 0.5),
        "Z11": (0.5, 1),
        "Z12": (1, 2),
        "Z13": (2, 3),
        "Z14": (3, 4),
        "Z15": (4, 5),
        "Z16": (5, 6),
        "Z17": (6, 7),
        "Z18": (7, 8),
        "Z19": (8, 9),
        "Z20": (9, 10),
        "Z21": (10, 11),
        "Z22": (11, 12),
        "Z23": (12, 13),
        "Z24": (13, 14),
        "Z25": (14, 15),
        "Z26": (15, 16),
        "Z27": (16, 17),
        "Z28": (17, 18),
        "Z29": (18, 20),
        "Z30": (20, 25)
}

# create a DataFrame with the zone names, lower and upper bounds
grade_zones_df = pd.DataFrame(grade.items(), columns=['zone', 'bounds'])
grade_zones_df[['lower', 'upper']] = pd.DataFrame(grade_zones_df['bounds'].tolist(), index=grade_zones_df.index)
grade_zones_df = grade_zones_df.drop('bounds', axis=1)

############################################ ELEVATION ZONE #############################

elevation = {
        "Z1": (0, 100),
        "Z2": (100, 200),
        "Z3": (200, 300),
        "Z4": (300, 400),
        "Z5": (400, 500),
        "Z6": (500, 600),
        "Z7": (600, 700),
        "Z8": (700, 800),
        "Z9": (800, 900),
        "Z10": (900, 1000),
        "Z11": (1000, 1500),
        "Z12": (1500, 2000),
        "Z13": (2000, 2500),
        "Z14": (2500, 3000),
        "Z15": (3000, 3500),
        "Z16": (3500, 4000),
        "Z17": (4000, 5000)
}

# create a DataFrame with the zone names, lower and upper bounds
elevation_zones_df = pd.DataFrame(elevation.items(), columns=['zone', 'bounds'])
elevation_zones_df[['lower', 'upper']] = pd.DataFrame(elevation_zones_df['bounds'].tolist(), index=elevation_zones_df.index)
elevation_zones_df = elevation_zones_df.drop('bounds', axis=1)
elevation_zones_df