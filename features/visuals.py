import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import datetime
from datetime import timedelta

import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
from plotly.graph_objects import Layout

import warnings
warnings.simplefilter("ignore", UserWarning)

from features.utils import *
from features.athlete_profile import *

############################################################# LOAD DATA ########################################################################

def activity_dive_in_dataset(zone_df, athlete_df, date):
    """
    Create a dataset for a given activity with all the need columns.

    Args:
        df_activities: path of the activities dataset.
        zone_df: path of the zone dataset.
        athlete_df: path of the athlete profile dataset.
        date: date of the activity to analyze.

    Returns:
        visual_df: visual data frame
    """

    df_act = loadData()
    df_zone = pd.read_csv(zone_df, index_col='Unnamed: 0')
    df_athlete = pd.read_csv(athlete_df, index_col='Unnamed: 0')

    df_act = df_act[df_act['Date'] == date]
    df_zone = df_zone[df_zone['Date'] == date]
    df_athlete = df_athlete[df_athlete['Date'] == date]

    #check that date exists
    if df_act.empty:
        print(f"Date {date} not found in activity data.")
        return
    else:
        ### Merge
        df_activity_visual = df_zone.merge(df_act[['Nom du fichier', 'Temps écoulé', 'Dénivelé positif', 'Dénivelé négatif', 'Altitude min.',
        'Altitude max.', 'Pente max.', 'Pente moyenne', 'Cadence max.']], how='left', on=['Nom du fichier'])
        df_activity_visual = df_activity_visual.merge(df_athlete[['Nom du fichier', 'new_relative_effort', 'TSS', 'HRR', 'trimp', 'HRSS',
        'Fitness', 'Fitness Diff', 'Fatigue', 'Fatigue Diff', 'Form']], how='left', on=['Nom du fichier'])
        
        #Get matching csv
        for index, row in df_activity_visual.iterrows():
            
            # Extract activity id from the file name column
            if "Nom du fichier" in row:
                activity_num = str(row["Nom du fichier"]).split("/")[-1].split(".")[0]
                # Load the activity data
                activity_file = f"data/activities_csv/{activity_num}.csv"
            else:
                activity_num = row['nom']
                activity_file = f"data/activities_csv/{activity_num}.csv"
                
            csv_data = pd.read_csv(activity_file)
            csv_data['enhanced_speed'] = csv_data['enhanced_speed']*3.6
        
        return df_activity_visual, csv_data

########################################################## MAP ################################################################################

import pandas as pd
import plotly.express as px

# Define a function to convert fixed-point coordinates to latitude and longitude in degrees
def fixed_to_degrees(value):
    degrees = float(value) / ((2**32) / 360)
    return degrees

def plot_map(data_file):
    """Plots latitude and longitude data from a CSV file on a map using Plotly Express.

    Args:
        data_file (str): The path to the CSV file containing the latitude and longitude data.

    Returns:
        None
    """

    # Read in the data from the CSV file
    data_source = data_file
    
    # Check if latitude and longitude are in the columns
    if 'latitude' in data_source.columns and 'longitude' in data_source.columns:
        # If latitude and longitude are present, calculate the center point and plot the data using Plotly Express
        center_lat = data_source['latitude'].mean()
        center_lon = data_source['longitude'].mean()
        fig = px.scatter_mapbox(data_source, 
                                lat="latitude", 
                                lon="longitude", 
                                zoom=10,
                                center=dict(lat=center_lat, lon=center_lon),
                                height=800,
                                width=800)
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
    else:
        # If latitude and longitude are not present, check if position_lat and position_long are in the columns
        if 'position_lat' in data_source.columns and 'position_long' in data_source.columns:
            # If position_lat and position_long are present, convert the values to degrees, calculate the center point, and plot the data
            data_source['latitude'] = data_source['position_lat'].apply(lambda x: fixed_to_degrees(x))
            data_source['longitude'] = data_source['position_long'].apply(lambda x: fixed_to_degrees(x))
            center_lat = data_source['latitude'].mean()
            center_lon = data_source['longitude'].mean()
            fig = px.scatter_mapbox(data_source, 
                                    lat="latitude", 
                                    lon="longitude", 
                                    zoom=10,
                                    center=dict(lat=center_lat, lon=center_lon),
                                    height=800,
                                    width=800)
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            
        else:
            # If latitude, longitude, position_lat, and position_long are not present, print an error message
            print('Error: latitude and longitude, or position_lat and position_long, columns not found in data')

    return fig

########################################################### HEART RATE ZONES ####################################################################

def plot_hr_zones(df_activity_visual, max_HR=190):
    """
    Plots a bar chart of the time spent in each HR zone, with a table of the time spent and percentage of time spent
    in each zone.

    Args:
        max_HR (int): athlete max heart rate.
        df_activity_visual (pd.DataFrame): DataFrame containing activity data, including time spent in each HR zone.

    Returns:
        visuals
    """

    #Calculate zones based on max HR
    RE_hr_data = calculate_hr_zones_elevate(max_HR)

    # Create a dictionary to map zone names to their corresponding bounds
    zone_bounds = dict(zip(RE_hr_data['Name'], RE_hr_data[['Lower Bound', 'Upper Bound']]))

    # Multiply the zone times by the duration to get the total time in each zone
    zone_times = [df_activity_visual['Durée de déplacement'].iloc[0] * df_activity_visual['time_z{}'.format(i)].iloc[0] for i in range(1, 7)]

    # Create a list of formatted time strings
    time_strings = []
    for t in zone_times:
        td = timedelta(minutes=t)
        time_str = (datetime(1, 1, 1) + td).strftime('%H:%M:%S')
        time_strings.append(time_str)

    # Create a list of zone labels for hover text
    zone_names = [f"Z{i+1}: {zone['Lower Bound']}-{zone['Upper Bound']} bpm" for i, zone in RE_hr_data.iterrows()]

    # Create a bar plot of the time spent in each HR zone using plotly
   
    fig1 = go.Figure(data=[go.Bar(
                x=zone_names, y=zone_times,
                marker_color='rgb(255, 216, 177)',  # set color of bars
                hovertemplate='<b>%{x}</b><br>' +
                            'Zone held during %{customdata}<br>' +
                            '<extra></extra>',
                customdata=time_strings
    )])

   
    fig1.update_layout(title='', xaxis_title='', yaxis_title='', height=600)


    # Create table with time and percentage for each HR zone
    zone_labels = ['Zone ' + str(i) for i in range(1, 7)]
    zone_ranges = [f"{zone['Range']}" for _, zone in RE_hr_data.iterrows()]
    zone_percentages = [df_activity_visual['time_z{}'.format(i)].iloc[0] * 100 for i in range(1, 7)]
    zone_percentages_str = [f"{p:.1f}%" for p in zone_percentages]
    table_data = {
        'Zone': zone_labels,
        'BPM Range': zone_ranges,
        'Time': time_strings,
        'Percentage': zone_percentages_str
    }

    fig2 = go.Figure(data=[go.Table(
        header=dict(values=['Zone', 'BPM Range', 'Time', 'Percentage'],
                    fill_color='antiquewhite',
                    align='left'),
        cells=dict(values=list(table_data.values()),
                   fill_color='white',
                   align='left'))
    ])
    fig2.update_layout(height=600)

    # Create subplots for the bar chart and table
    fig = sp.make_subplots(rows=1, cols=2,
                            column_widths=[0.6, 0.4],
                            specs=[[{"type": "bar"},
                                    {"type": "table"}]])

    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig2.data[0], row=1, col=2)

    fig.update_yaxes(showgrid=True, gridwidth=1, linecolor='black', gridcolor='lightgrey')
    fig.update_xaxes(showgrid=True, linecolor='black')

    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=400, plot_bgcolor='rgba(0,0,0,0)')

    return fig


################################################################## SPEED ZONES ###########################################################

def calculate_time_in_speed_zones(df_activity_visual, speed_zones=speed):
    """
    Calculate the time spent in each power zone for each activity and add the results as columns.
    
    Args:
    - df_activity_visual (pandas.DataFrame): A DataFrame containing information about the activity.
    - speed_zones (list): list of speed_speed_zones
    
    Returns:
    - df_activity_visual (pandas.DataFrame): The original DataFrame with new columns for the time spent in each speed zone.
    """
    df_activity_visual = df_activity_visual.drop(['time_z1', 'avgHR_z1', 'time_z2', 'avgHR_z2', 'time_z3', 'avgHR_z3', 'time_z4', 'avgHR_z4', 'time_z5', 'avgHR_z5', 'time_z6', 'avgHR_z6'], axis=1)
    
    # Loop through the rows in df and calculate time spent in each zone for the corresponding activity
    for index, row in df_activity_visual.iterrows():
        
        # Extract activity id from the file name column
        if "Nom du fichier" in row:
            activity_num = str(row["Nom du fichier"]).split("/")[-1].split(".")[0]
            # Load the activity data
            activity_file = f"data/activities_csv/{activity_num}.csv"
        else:
            activity_num = row['nom']
            activity_file = f"data/activities_csv/{activity_num}.csv"
            
        csv_data = pd.read_csv(activity_file)
        csv_data['enhanced_speed'] = csv_data['enhanced_speed']*3.6
        
        # Calculate the time spent in each zone
        time_in_zone = {zone: 0 for zone in speed_zones}
        for _, row in csv_data.iterrows():
            speed = row["enhanced_speed"]
            for zone, (lower, upper) in speed_zones.items():
                if lower <= speed < upper:
                    time_in_zone[zone] += 1
        
        # Calculate the percentage of time spent in each zone
        total_time = len(csv_data)
        percent_time_in_zone = {zone: round(time / total_time, 4) for zone, time in time_in_zone.items()}
        
        # Add new columns with time spent in each zone to df_activity_visual
        for zone, percent_time in percent_time_in_zone.items():
            column_name = f"time_{zone.lower()}"
            df_activity_visual.loc[index, column_name] = percent_time
    
    return df_activity_visual


def plot_speed_zones(df, speed_zones_list=speed, speed_zones_df=speed_zones_df):
    """
    Plots a bar chart of the time spent in each speed zone, with a table of the time spent and percentage of time spent
    in each zone.

    Args:
        speed_zones (pd.DataFrame): DataFrame containing speed zone data, including zone name, lower and upper bounds.
        speed_zones_df (pd.DataFrame): DataFrame containing speed zone data, including zone name, lower and upper bounds.

    Returns:
        visuals
    """

    speed_zones = calculate_time_in_speed_zones(df)

    # Multiply the zone times by the duration to get the total time in each zone
    zone_times = [speed_zones['Durée de déplacement'].iloc[0] *speed_zones['time_z{}'.format(i)].iloc[0] for i in range(1, 18)]

    # Create a list of formatted time strings
    time_strings = []
    for t in zone_times:
        td = timedelta(minutes=t)
        time_str = (datetime(1, 1, 1) + td).strftime('%M:%S')
        time_strings.append(time_str)
    time_strings

    #Create a list of zone labels for hover text
    zone_names = [f"Z{i+1}: {zone['lower']}-{zone['upper']} bpm" for i, zone in speed_zones_df.iterrows()]

    # Create a bar plot of the time spent in each speed zone using plotly
    fig1 = go.Figure(data=[go.Bar(
                x=zone_names, y=zone_times,
                marker_color='rgb(175, 207, 255)',
                hovertemplate='<b>%{x}</b><br>' +
                            'Zone held during %{customdata}<br>' +
                            '<extra></extra>',
                customdata=time_strings
    )])
    fig1.update_layout(title='Time spent in each speed zone', xaxis_title='', yaxis_title='', height=600)

    # Create table with time and percentage for each speed zone
    zone_labels = ['Zone ' + str(i) for i in range(1, 18)]
    zone_from =  [f"{zone['lower']}" for _, zone in speed_zones_df.iterrows()]
    zone_to =  [f"{zone['upper']}" for _, zone in speed_zones_df.iterrows()]
    zone_percentages = [speed_zones['time_z{}'.format(i)].iloc[0] * 100 for i in range(1, 18)]
    zone_percentages_str = [f"{p:.1f}%" for p in zone_percentages]
    table_data = {
        'Zone': zone_labels,
        'From KPH': zone_from,
        'To KPH': zone_to,
        'Time': time_strings,
        'Percentage': zone_percentages_str
    }

    fig2 = go.Figure(data=[go.Table(
        header=dict(values=['Zone', 'From KPH', 'To KPH', 'Time', 'Percentage'],
                    fill_color='antiquewhite',
                    align='left'),
        cells=dict(values=list(table_data.values()),
                   fill_color='white',
                   align='left'))
    ])
    fig2.update_layout(height=600)

    # Create subplots for the bar chart and table
    fig = sp.make_subplots(rows=1, cols=2,
                            column_widths=[0.6, 0.4],
                            specs=[[{"type": "bar"},
                                    {"type": "table"}]])

    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig2.data[0], row=1, col=2)

    fig.update_yaxes(showgrid=True, gridwidth=1, linecolor='black', gridcolor='lightgrey')
    fig.update_xaxes(showgrid=True, linecolor='black')


    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=500, plot_bgcolor='rgba(0,0,0,0)')

    return fig

############################################################ POWER ###############################################################

def calculate_time_in_power_watt_zones(df_activity_visual, power_zones=power):
    """
    Calculate the time spent in each power zone for each activity and add the results as columns.
    
    Args:
    - df_activity_visual (pandas.DataFrame): A DataFrame containing information about the activity.
    -power_power_zones (list): list of power power_zones
    
    Returns:
    - df_activity_visual (pandas.DataFrame): The original DataFrame with new columns for the time spent in each power zone.
    """

    
    # Loop through the rows in df and calculate time spent in each zone for the corresponding activity
    for index, row in df_activity_visual.iterrows():
        
        # Extract activity id from the file name column
        if "Nom du fichier" in row:
            activity_num = str(row["Nom du fichier"]).split("/")[-1].split(".")[0]
            # Load the activity data
            activity_file = f"data/activities_csv/{activity_num}.csv"
        else:
            activity_num = row['nom']
            activity_file = f"data/activities_csv/{activity_num}.csv"
            
        csv_data = pd.read_csv(activity_file)
        
        # Calculate the time spent in each zone
        time_in_zone = {zone: 0 for zone in power_zones}
        for _, row in csv_data.iterrows():
            power = row["power"]
            for zone, (lower, upper) in power_zones.items():
                if lower <= power < upper:
                    time_in_zone[zone] += 1
        
        # Calculate the percentage of time spent in each zone
        total_time = len(csv_data)
        percent_time_in_zone = {zone: round(time / total_time, 4) for zone, time in time_in_zone.items()}
        
        # Add new columns with time spent in each zone to df_activity_visual
        for zone, percent_time in percent_time_in_zone.items():
            column_name = f"time_{zone.lower()}"
            df_activity_visual.loc[index, column_name] = percent_time
    
    return df_activity_visual


def plot_power_zones(df, power_zones_list=power, power_zones_df=power_zones_df):
    """
    Plots a bar chart of the time spent in each power zone, with a table of the time spent and percentage of time spent
    in each zone.

    Args:
        power_zones (pd.DataFrame): DataFrame with the activity data and the calculated time spent in each zone.
        power_zones_df (pd.DataFrame): DataFrame containing power zone data, including zone name, lower and upper bounds.

    Returns:
        visuals
    """
    power_zones = calculate_time_in_power_watt_zones(df)

    # Multiply the zone times by the duration to get the total time in each zone
    zone_times = [power_zones['Durée de déplacement'].iloc[0] *power_zones['time_z{}'.format(i)].iloc[0] for i in range(1, 20)]

    # Create a list of formatted time strings
    time_strings = []
    for t in zone_times:
        td = timedelta(minutes=t)
        time_str = (datetime(1, 1, 1) + td).strftime('%M:%S')
        time_strings.append(time_str)
    time_strings

    #Create a list of zone labels for hover text
    zone_names = [f"Z{i+1}: {zone['lower']}-{zone['upper']} bpm" for i, zone in power_zones_df.iterrows()]

    # Create a bar plot of the time spent in each power zone using plotly
    fig1 = go.Figure(data=[go.Bar(
                x=zone_names, y=zone_times,
                marker_color='rgb(230, 230, 230)',
                hovertemplate='<b>%{x}</b><br>' +
                            'Zone held during %{customdata}<br>' +
                            '<extra></extra>',
                customdata=time_strings
    )])
    fig1.update_layout(title='Time spent in each power zone', xaxis_title='', yaxis_title='', height=600)

    # Create table with time and percentage for each power zone
    zone_labels = ['Zone ' + str(i) for i in range(1, 20)]
    zone_from =  [f"{zone['lower']}" for _, zone in power_zones_df.iterrows()]
    zone_to =  [f"{zone['upper']}" for _, zone in power_zones_df.iterrows()]
    zone_percentages = [power_zones['time_z{}'.format(i)].iloc[0] * 100 for i in range(1, 20)]
    zone_percentages_str = [f"{p:.1f}%" for p in zone_percentages]
    table_data = {
        'Zone': zone_labels,
        'From W': zone_from,
        'To W': zone_to,
        'Time': time_strings,
        'Percentage': zone_percentages_str
    }

    fig2 = go.Figure(data=[go.Table(
        header=dict(values=['Zone', 'From W', 'To W', 'Time', 'Percentage'],
                    fill_color='antiquewhite',
                    align='left'),
        cells=dict(values=list(table_data.values()),
                   fill_color='white',
                   align='left'))
    ])
    fig2.update_layout(height=600)

    # Create subplots for the bar chart and table
    fig = sp.make_subplots(rows=1, cols=2,
                            column_widths=[0.6, 0.4],
                            specs=[[{"type": "bar"},
                                    {"type": "table"}]])

    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig2.data[0], row=1, col=2)

    fig.update_yaxes(showgrid=True, gridwidth=1, linecolor='black', gridcolor='lightgrey')
    fig.update_xaxes(showgrid=True, linecolor='black')


    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=550, plot_bgcolor='rgba(0,0,0,0)')

    return fig

def plot_power_curve(df_activity_visual, df_data):
    """
    Plots the Power Curve for a given ride.

    Parameters:
    -----------
    df_activity_visual: pandas DataFrame
        DataFrame with the activity details including 'Durée de déplacement' column in minutes.
    df_data: pandas DataFrame
        DataFrame with the activity data including 'timestamp' and 'activity_id' columns.

    Returns:
    --------
    None: plots a line graph of the Power Curve with a table.
    """

    # Step 2: Convert the ride duration from minutes to seconds
    ride_duration = df_activity_visual['Durée de déplacement'] * 60

    # Step 3: Calculate the rolling average power for each time period
    df_data['timestamp'] = pd.to_datetime(df_data['timestamp'])
    data_rolling = df_data.copy()
    data_rolling.set_index('timestamp', inplace=True)

    # Resample the data to 1-second intervals
    data_rolling = data_rolling.resample('1S').mean()

    rolling_periods = [1, 2, 3, 5, 10, 20, 30, 60, 120, 300, 600, 1200, 1800, 3600, 7200]
    rolling_power = {p: data_rolling['power'].rolling(window=p, min_periods=1).mean() for p in rolling_periods}

    # Step 4: Find the maximum rolling average power for each time period
    max_rolling_power = [rp.max() for rp in rolling_power.values()]

    # Step 5: Plot the results in a line graph
    fig = px.line(x=rolling_periods, y=max_rolling_power, log_x=True, labels={
                  'x': 'Time (seconds)', 'y': 'Power (watts)'})
    
    # set the line color to light grey
    fig.update_traces(line=dict(color='rgb(200, 200, 200)'))

    # Format x-axis with time
    fig.update_xaxes(
        tickvals=[1, 2, 3, 5, 10, 20, 30, 60, 120, 300, 600, 1200, 3600, 7200],
        ticktext=['00:01', '00:02', '00:03', '00:05', '00:10', '00:20', '00:30', '01:00', '02:00', '05:00', '10:00', '20:00', '30:00', '1:00:00', '2:00:00'],
        tickangle=0,
        dtick=1
    )

    fig.update_yaxes(showgrid=True, gridwidth=1, linecolor='black', gridcolor='lightgrey')
    fig.update_xaxes(showgrid=True, linecolor='black')


    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=500, plot_bgcolor='rgba(0,0,0,0)')

    return fig

####################################################################### CADENCE ##############################################################

def calculate_time_in_cadence_zones(df_activity_visual, cadence_zones=cadence):
    """
    Calculate the time spent in each cadence zone for each activity and add the results as columns.
    
    Args:
    - df_activity_visual (pandas.DataFrame): A DataFrame containing information about the activity.
    -cadence_zones (list): list of cadence zones
    
    Returns:
    - df_activity_visual (pandas.DataFrame): The original DataFrame with new columns for the time spent in each cadence zone.
    """

    
    # Loop through the rows in df and calculate time spent in each zone for the corresponding activity
    for index, row in df_activity_visual.iterrows():
        
        # Extract activity id from the file name column
        if "Nom du fichier" in row:
            activity_num = str(row["Nom du fichier"]).split("/")[-1].split(".")[0]
            # Load the activity data
            activity_file = f"data/activities_csv/{activity_num}.csv"
        else:
            activity_num = row['nom']
            activity_file = f"data/activities_csv/{activity_num}.csv"
            
        csv_data = pd.read_csv(activity_file)
        
        # Calculate the time spent in each zone
        time_in_zone = {zone: 0 for zone in cadence_zones}
        for _, row in csv_data.iterrows():
            cadence = row["cadence"]
            for zone, (lower, upper) in cadence_zones.items():
                if lower <= cadence < upper:
                    time_in_zone[zone] += 1
        
        # Calculate the percentage of time spent in each zone
        total_time = len(csv_data)
        percent_time_in_zone = {zone: round(time / total_time, 4) for zone, time in time_in_zone.items()}
        
        # Add new columns with time spent in each zone to df_activity_visual
        for zone, percent_time in percent_time_in_zone.items():
            column_name = f"time_{zone.lower()}"
            df_activity_visual.loc[index, column_name] = percent_time
    
    return df_activity_visual


def plot_cadence_zones(df_activity_visual, cadence_zones=cadence, cadence_zones_df=cadence_zones_df):
    """
    Plots a bar chart of the time spent in each cadence zone, with a table of the time spent and percentage of time spent
    in each zone.

    Args:
        cadence_zones (pd.DataFrame): DataFrame with the activity data and the calculated time spent in each zone.
        cadence_zones_df (pd.DataFrame): DataFrame containing cadence zone data, including zone name, lower and upper bounds.

    Returns:
        visuals
    """
    #Create time in cadence zones df 
    cadence_zones = calculate_time_in_cadence_zones(df_activity_visual, cadence_zones)

    # Multiply the zone times by the duration to get the total time in each zone
    zone_times = [cadence_zones['Durée de déplacement'].iloc[0] *cadence_zones['time_z{}'.format(i)].iloc[0] for i in range(1, 26)]

    # Create a list of formatted time strings
    time_strings = []
    for t in zone_times:
        td = timedelta(minutes=t)
        time_str = (datetime(1, 1, 1) + td).strftime('%M:%S')
        time_strings.append(time_str)
    time_strings

    #Create a list of zone labels for hover text
    zone_names = [f"Z{i+1}: {zone['lower']}-{zone['upper']} bpm" for i, zone in cadence_zones_df.iterrows()]

    # Create a bar plot of the time spent in each cadence zone using plotly
    fig1 = go.Figure(data=[go.Bar(
                x=zone_names, y=zone_times,
                 marker_color='rgb(102, 51, 153)',
                hovertemplate='<b>%{x}</b><br>' +
                            'Zone held during %{customdata}<br>' +
                            '<extra></extra>',
                customdata=time_strings
    )])
    fig1.update_layout(title='Time spent in each cadence zone', xaxis_title='', yaxis_title='', height=600)

    # Create table with time and percentage for each cadence zone
    zone_labels = ['Zone ' + str(i) for i in range(1, 26)]
    zone_from =  [f"{zone['lower']}" for _, zone in cadence_zones_df.iterrows()]
    zone_to =  [f"{zone['upper']}" for _, zone in cadence_zones_df.iterrows()]
    zone_percentages = [cadence_zones['time_z{}'.format(i)].iloc[0] * 100 for i in range(1, 26)]
    zone_percentages_str = [f"{p:.1f}%" for p in zone_percentages]
    table_data = {
        'Zone': zone_labels,
        'From RPM': zone_from,
        'To RPM': zone_to,
        'Time': time_strings,
        'Percentage': zone_percentages_str
    }

    fig2 = go.Figure(data=[go.Table(
        header=dict(values=['Zone', 'From RPM', 'To RPM', 'Time', 'Percentage'],
                    fill_color='antiquewhite',
                    align='left'),
        cells=dict(values=list(table_data.values()),
                   fill_color='white',
                   align='left'))
    ])
    fig2.update_layout(height=600)

    # Create subplots for the bar chart and table
    fig = sp.make_subplots(rows=1, cols=2,
                            column_widths=[0.7, 0.4],
                            specs=[[{"type": "bar"},
                                    {"type": "table"}]])

    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig2.data[0], row=1, col=2)

    fig.update_yaxes(showgrid=True, gridwidth=1, linecolor='black', gridcolor='lightgrey')
    fig.update_xaxes(showgrid=True, linecolor='black')
    fig.update_xaxes(tickangle=-45)

    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=650, plot_bgcolor='rgba(0,0,0,0)')

    return fig

############################################################ ELEVATION ################################################################
def calculate_time_in_elevation_zones(df, elevation_zones=elevation):
    """
    Calculate the time spent in each elevation zone for each activity and add the results as columns.
    
    Args:
    - df (pandas.DataFrame): A DataFrame containing information about the activity.
    -elevation_zones (list): list of elevation zones
    
    Returns:
    - df (pandas.DataFrame): The original DataFrame with new columns for the time spent in each elevation zone.
    """

    
    # Loop through the rows in df and calculate time spent in each zone for the corresponding activity
    for index, row in df.iterrows():
        
        # Extract activity id from the file name column
        if "Nom du fichier" in row:
            activity_num = str(row["Nom du fichier"]).split("/")[-1].split(".")[0]
            # Load the activity data
            activity_file = f"data/activities_csv/{activity_num}.csv"
        else:
            activity_num = row['nom']
            activity_file = f"data/activities_csv/{activity_num}.csv"
            
        csv_data = pd.read_csv(activity_file)
        
        # Calculate the time spent in each zone
        time_in_zone = {zone: 0 for zone in elevation_zones}
        for _, row in csv_data.iterrows():
            elevation = row["altitude"]
            for zone, (lower, upper) in elevation_zones.items():
                if lower <= elevation < upper:
                    time_in_zone[zone] += 1
        
        # Calculate the percentage of time spent in each zone
        total_time = len(csv_data)
        percent_time_in_zone = {zone: round(time / total_time, 4) for zone, time in time_in_zone.items()}
        
        # Add new columns with time spent in each zone to df
        for zone, percent_time in percent_time_in_zone.items():
            column_name = f"time_{zone.lower()}"
            df.loc[index, column_name] = percent_time
    
    return df

def plot_elevation_zones(df, elevation_zones=elevation, elevation_zones_df=elevation_zones_df):
    """
    Plots a bar chart of the time spent in each elevation zone, with a table of the time spent and percentage of time spent
    in each zone.

    Args:
        elevation_zones (pd.DataFrame): DataFrame with the activity data and the calculated time spent in each zone.
        elevation_zones_df (pd.DataFrame): DataFrame containing elevation zone data, including zone name, lower and upper bounds.

    Returns:
        visuals
    """
    #Create time in elevation zones df 
    elevation_zones = calculate_time_in_elevation_zones(df, elevation_zones)

    # Multiply the zone times by the duration to get the total time in each zone
    zone_times = [elevation_zones['Durée de déplacement'].iloc[0] *elevation_zones['time_z{}'.format(i)].iloc[0] for i in range(1, 18)]

    # Create a list of formatted time strings
    time_strings = []
    for t in zone_times:
        td = timedelta(minutes=t)
        time_str = (datetime(1, 1, 1) + td).strftime('%M:%S')
        time_strings.append(time_str)
    time_strings

    #Create a list of zone labels for hover text
    zone_names = [f"Z{i+1}: {zone['lower']}-{zone['upper']} m" for i, zone in elevation_zones_df.iterrows()]

    # Create a bar plot of the time spent in each elevation zone using plotly
    fig1 = go.Figure(data=[go.Bar(
                x=zone_names, y=zone_times,
                marker_color='rgb(205, 200, 0)',
                hovertemplate='<b>%{x}</b><br>' +
                            'Zone held during %{customdata}<br>' +
                            '<extra></extra>',
                customdata=time_strings
    )])
    fig1.update_layout(title='Time spent in each elevation zone', xaxis_title='', yaxis_title='', height=600)

    # Create table with time and percentage for each elevation zone
    zone_labels = ['Zone ' + str(i) for i in range(1, 18)]
    zone_from =  [f"{zone['lower']}" for _, zone in elevation_zones_df.iterrows()]
    zone_to =  [f"{zone['upper']}" for _, zone in elevation_zones_df.iterrows()]
    zone_percentages = [elevation_zones['time_z{}'.format(i)].iloc[0] * 100 for i in range(1, 18)]
    zone_percentages_str = [f"{p:.1f}%" for p in zone_percentages]
    table_data = {
        'Zone': zone_labels,
        'From M': zone_from,
        'To M': zone_to,
        'Time': time_strings,
        'Percentage': zone_percentages_str
    }

    fig2 = go.Figure(data=[go.Table(
        header=dict(values=['Zone', 'From M', 'To M', 'Time', 'Percentage'],
                    fill_color='antiquewhite',
                    align='left'),
        cells=dict(values=list(table_data.values()),
                   fill_color='white',
                   align='left'))
    ])
    fig2.update_layout(height=600)

    # Create subplots for the bar chart and table
    fig = sp.make_subplots(rows=1, cols=2,
                            column_widths=[0.7, 0.4],
                            specs=[[{"type": "bar"},
                                    {"type": "table"}]])

    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig2.data[0], row=1, col=2)

    fig.update_yaxes(showgrid=True, gridwidth=1, linecolor='black', gridcolor='lightgrey')
    fig.update_xaxes(showgrid=True, linecolor='black')
    fig.update_xaxes(tickangle=-45)

    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=450, plot_bgcolor='rgba(0,0,0,0)')

    return fig

def plot_elevation_profile(df):
    """
    This function plots an elevation profile chart with distance on the x-axis and altitude on the y-axis.
    
    Parameters:
    df (pandas.DataFrame): A pandas DataFrame with 'distance', 'altitude', and 'timestamp' columns.
    
    Returns:
    None: Displays the plot in the console.
    """
    df_elevation = df.sort_values('distance')
    # convert timestamp to datetime object
    df_elevation['timestamp'] = pd.to_datetime(df_elevation['timestamp'])
    # calculate elapsed time in minutes
    df_elevation['elapsed_time'] = (df_elevation['timestamp'] - df_elevation['timestamp'][0])
    
    df_elevation['time_elapsed'] = pd.to_timedelta(df_elevation['elapsed_time'], unit='s')
    df_elevation['time_elapsed_formatted'] = df_elevation['time_elapsed'].dt.components['hours'].map("{:02d}".format) + \
                                          ":" + df_elevation['time_elapsed'].dt.components['minutes'].map("{:02d}".format) + \
                                          ":" + df_elevation['time_elapsed'].dt.components['seconds'].map("{:02d}".format)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_elevation['distance']/1000, y=df_elevation['altitude'], 
                             marker_color='rgb(205, 200, 0)',
                             mode='lines', 
                             fill='tozeroy', 
                             name='', 
                             customdata=df_elevation[['time_elapsed_formatted', 'grade']]))

    fig.update_layout(
        title='Elevation Profile',
        xaxis_title='Distance (km)',
        yaxis_title='Altitude (m)',
        hovermode='closest'
    )

    fig.update_traces(hovertemplate='Time elapsed: %{customdata[0]}<br>Distance: %{x:.2f} km<br>Altitude: %{y:.0f} m<br>Grade: %{customdata[1]}')
    fig.update_yaxes(showgrid=True, gridwidth=1, linecolor='black', gridcolor='lightgrey')
    fig.update_xaxes(showgrid=True, linecolor='black')
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=450, plot_bgcolor='rgba(0,0,0,0)')

    return fig


############################################################ GRADE ################################################################

def calculate_time_in_grade_zones(df, grade_zones=grade):
    """
    Calculate the time spent in each grade zone for each activity and add the results as columns.
    
    Args:
    - df (pandas.DataFrame): A DataFrame containing information about the activity.
    -grade_zones (list): list of grade zones
    
    Returns:
    - df (pandas.DataFrame): The original DataFrame with new columns for the time spent in each grade zone.
    """

    
    # Loop through the rows in df and calculate time spent in each zone for the corresponding activity
    for index, row in df.iterrows():
        
        # Extract activity id from the file name column
        if "Nom du fichier" in row:
            activity_num = str(row["Nom du fichier"]).split("/")[-1].split(".")[0]
            # Load the activity data
            activity_file = f"data/activities_csv/{activity_num}.csv"
        else:
            activity_num = row['nom']
            activity_file = f"data/activities_csv/{activity_num}.csv"
            
        csv_data = pd.read_csv(activity_file)
        
        # Calculate the time spent in each zone
        time_in_zone = {zone: 0 for zone in grade_zones}
        for _, row in csv_data.iterrows():
            grade = row["grade"]
            for zone, (lower, upper) in grade_zones.items():
                if lower <= grade < upper:
                    time_in_zone[zone] += 1
        
        # Calculate the percentage of time spent in each zone
        total_time = len(csv_data)
        percent_time_in_zone = {zone: round(time / total_time, 4) for zone, time in time_in_zone.items()}
        
        # Add new columns with time spent in each zone to df
        for zone, percent_time in percent_time_in_zone.items():
            column_name = f"time_{zone.lower()}"
            df.loc[index, column_name] = percent_time
    
    return df


def plot_grade_zones(df, grade_zones=grade, grade_zones_df=grade_zones_df):
    """
    Plots a bar chart of the time spent in each grade zone, with a table of the time spent and percentage of time spent
    in each zone.

    Args:
        grade_zones (pd.DataFrame): DataFrame with the activity data and the calculated time spent in each zone.
        grade_zones_df (pd.DataFrame): DataFrame containing grade zone data, including zone name, lower and upper bounds.

    Returns:
        visuals
    """
    #Create time in grade zones df 
    grade_zones = calculate_time_in_grade_zones(df, grade_zones)

    # Multiply the zone times by the duration to get the total time in each zone
    zone_times = [grade_zones['Durée de déplacement'].iloc[0] *grade_zones['time_z{}'.format(i)].iloc[0] for i in range(1, 31)]

    # Create a list of formatted time strings
    time_strings = []
    for t in zone_times:
        td = timedelta(minutes=t)
        time_str = (datetime(1, 1, 1) + td).strftime('%M:%S')
        time_strings.append(time_str)
    time_strings

    #Create a list of zone labels for hover text
    zone_names = [f"Z{i+1}: {zone['lower']}-{zone['upper']} %" for i, zone in grade_zones_df.iterrows()]

    # Create a bar plot of the time spent in each grade zone using plotly
    fig1 = go.Figure(data=[go.Bar(
                x=zone_names, y=zone_times,
                marker_color='rgb(0, 128, 0)',
                hovertemplate='<b>%{x}</b><br>' +
                            'Zone held during %{customdata}<br>' +
                            '<extra></extra>',
                customdata=time_strings
    )])
    fig1.update_layout(title='Time spent in each grade zone', xaxis_title='', yaxis_title='', height=600)

    # Create table with time and percentage for each grade zone
    zone_labels = ['Zone ' + str(i) for i in range(1, 31)]
    zone_from =  [f"{zone['lower']}" for _, zone in grade_zones_df.iterrows()]
    zone_to =  [f"{zone['upper']}" for _, zone in grade_zones_df.iterrows()]
    zone_percentages = [grade_zones['time_z{}'.format(i)].iloc[0] * 100 for i in range(1, 31)]
    zone_percentages_str = [f"{p:.1f}%" for p in zone_percentages]
    table_data = {
        'Zone': zone_labels,
        'From M': zone_from,
        'To M': zone_to,
        'Time': time_strings,
        'Percentage': zone_percentages_str
    }

    fig2 = go.Figure(data=[go.Table(
        header=dict(values=['Zone', 'From M', 'To M', 'Time', 'Percentage'],
                    fill_color='antiquewhite',
                    align='left'),
        cells=dict(values=list(table_data.values()),
                   fill_color='white',
                   align='left'))
    ])
    fig2.update_layout(height=600)

    # Create subplots for the bar chart and table
    fig = sp.make_subplots(rows=1, cols=2,
                            column_widths=[0.7, 0.4],
                            specs=[[{"type": "bar"},
                                    {"type": "table"}]])

    fig.add_trace(fig1.data[0], row=1, col=1)
    fig.add_trace(fig2.data[0], row=1, col=2)

    fig.update_yaxes(showgrid=True, gridwidth=1, linecolor='black', gridcolor='lightgrey')
    fig.update_xaxes(showgrid=True, linecolor='black')
    fig.update_xaxes(tickangle=-45)

    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=750, plot_bgcolor='rgba(0,0,0,0)')

    return fig
