import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import plotly.graph_objs as go

from features.utils import *
from features.athlete_profile import *

def calculate_fitness_fatigue_form(data="data/zone_data_subdiv.csv"):
    """
    Generates a plot of the Fatigue, Fitness, and Form scores over the last 'time_offset' months using data from the specified CSV file.
    Args:
    - data (str): The path to the CSV file containing the data. Default value is "data/zone_data_subdiv.csv".
    - time_offset (int): The number of months of data to include in the plot. Default value is 6.

    Returns:
    - fig (plotly.graph_objs._figure.Figure): A plotly figure object containing the Fatigue, Fitness, and Form scores plotted over the last 'time_offset' months.
    """

    #load data
    zone_data = pd.read_csv(data, index_col="Unnamed: 0")

    #add new relative effort measure
    zone_data = calculate_new_relative_effort(zone_data)
    #add TSS measure
    zone_data = training_load_measure(zone_data, 405)
    #add HRR
    zone_data = HRR(zone_data, 65, 190)
    #add TRIMP
    zone_data = trimp(zone_data)
    #add Stress Score
    zone_data = HRSS(zone_data)
    #add fitness
    zone_data = calculate_fitness(zone_data)[0]
    #add fatigue
    zone_data = calculate_fatigue(zone_data)[0]
    #add form
    zone_data = calculate_form(zone_data)

    return zone_data

def fitness_fatigue_form_graph(data="data/zone_data_subdiv.csv", time_offset: int = 6):
    """
    Generates a plot of the Fatigue, Fitness, and Form scores over the last 'time_offset' months using data from the specified CSV file.
    Args:
    - data (str): The path to the CSV file containing the data. Default value is "data/zone_data_subdiv.csv".
    - time_offset (int): The number of months of data to include in the plot. Default value is 6.

    Returns:
    - fig (plotly.graph_objs._figure.Figure): A plotly figure object containing the Fatigue, Fitness, and Form scores plotted over the last 'time_offset' months.
    """

    #add metrics
    zone_data = calculate_fitness_fatigue_form(data)

    #plot fitness fatigue form graph
    fig = go.Figure()

    zone_data['Date'] = pd.to_datetime(zone_data['Date'])

    # Select data from the last 'time_offset' months
    time_offset_ago = pd.Timestamp.today() - pd.DateOffset(months=time_offset)
    last_time_offset = zone_data[zone_data['Date'] >= time_offset_ago]

    # Add Fatigue line
    fig.add_trace(go.Scatter(x=last_time_offset['Date'], y=last_time_offset['Fatigue'], name='Fatigue', line=dict(color='blue'),
                              hovertemplate='Fatigue: %{y:.2f} (%{customdata[0]:.2f})<extra></extra>',
                              customdata=np.stack((last_time_offset['Fatigue Diff'],), axis=-1)))

    # Add Fitness line
    fig.add_trace(go.Scatter(x=last_time_offset['Date'], y=last_time_offset['Fitness'], name='Fitness', line=dict(color='darkorange'),
                              hovertemplate='Fitness: %{y:.2f} (%{customdata[0]:.2f})<extra></extra>',
                              customdata=np.stack((last_time_offset['Fitness Diff'],), axis=-1)))

    # Add Form line
    fig.add_trace(go.Scatter(x=last_time_offset['Date'], y=last_time_offset['Form'], name='Form', fill='tozeroy', line=dict(color='lightgreen'),
                              hovertemplate='Form: %{y:.2f}<extra></extra>'))

    # Set x-axis label and title
    fig.update_xaxes(title_text='', showspikes = True,
                     spikemode  = 'across+toaxis',
                     spikesnap = 'cursor',
                     spikecolor='black',
                     spikethickness=2,
                     showline=True,
                     showgrid=True)

    # Set y-axis label and title
    fig.update_yaxes(title_text='Score')

   

    # Set chart title
    fig.update_yaxes(showgrid=True, gridwidth=1, linecolor='black', gridcolor='lightgrey')
    fig.update_xaxes(showgrid=True, linecolor='black')
    fig.update_layout(title='Fatigue, Fitness, and Form over the Last {} Months'.format(time_offset),
                      margin=dict(l=10, r=10, t=50, b=10), height=450,plot_bgcolor='rgba(0,0,0,0)',
                      hovermode='x',
                      hoverlabel=dict(bgcolor="lightgrey", font_size=12),
                      hoverdistance=50)

    # Show the plot
    return fig

def predict_fitness_fatigue_form(duration, distance, avg_hr, df="data/zone_data_subdiv.csv", ftp=405, resting_hr=65, max_hr=190, lthr=172):
    """
    Calculate fitness, fatigue, and form based on activity duration, distance, and average heart rate.

    Args:
        duration (float): Activity duration in minutes.
        distance (float): Activity distance in kilometers.
        avg_hr (float): Average heart rate during activity.
        ftp (float): Athlete Functional Threshold Power. Default is 405.
        resting_hr (float): Athlete resting heart rate. Default is 65.
        max_hr (float): Athlete max heart rate. Default is 190.
        lthr (float): Athlete Lactate Threshold Heart Rate. Default is 172.

    Returns:
        Tuple[float, float, float]: Fitness, fatigue, and form scores.
    """
    zone_data = calculate_fitness_fatigue_form(df)
    
    # Calculate Heart Rate Reserve (HRR)
    hrr = (avg_hr - resting_hr) / (max_hr - resting_hr)
    
    # Calculate Training Impulse (TRIMP)
    trimp = duration * hrr * 0.64 * np.exp(1.92 * hrr)
    
    # Calculate Hourly TRIMP at Lactate Threshold
    hrr_lthr = (lthr - resting_hr) / (max_hr - resting_hr)
    hour_trimp_lthr = 60*hrr_lthr*0.64*np.exp(1.92*hrr_lthr)
    
    # Calculate Heart Rate Stress Score (HRSS)
    hrss = (trimp / hour_trimp_lthr) * 100


    previous_fatigue = zone_data.iloc[-1]['Fatigue']
    previous_fitness = zone_data.iloc[-1]['Fitness']
    
    # Calculate Fitness, Fatigue, and Form
    fitness = round(previous_fitness + (hrss - previous_fitness) * (1 - math.exp(-1/42)),2)
    fitness_diff = round(fitness - previous_fitness,2)
    fatigue = round(previous_fatigue + (hrss - previous_fatigue) * (1 - math.exp(-1/7)),2)
    fatigue_diff = round(fatigue - previous_fatigue,2)
    
    return print(f"A workout of {distance} kms, during {duration} minutes at an average Heart Rate of {avg_hr} will have the following impact:\n\n\033[1m-Fitness Score:\033[0m {fitness} ({fitness_diff})\n\033[1m-Fatigue Score:\033[0m {fatigue} ({fatigue_diff})")
