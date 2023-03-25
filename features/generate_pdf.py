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

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
import plotly.io as pio
from reportlab.lib.units import inch

import warnings
warnings.simplefilter("ignore", UserWarning)

from features.utils import *
from features.athlete_profile import *
from features.visuals import *


def generate_activity_pdf(date="2023-02-18", saving_name ='activity_metrics.pdf'):
    """
    Function that takes in an activity date and a path and generate a PDF with all of the activity metrics and analyses.

    Args:
    - data (datetime): activity date.
    - saving_name (str): name to give the pdf
    
    Returns:
    - df_activity_visual (pandas.DataFrame): The original DataFrame with new columns for the time spent in each speed zone.
    """
    #load data
    df_activity_visual = activity_dive_in_dataset('data/zone_data_6.csv', 'data/athlete_profile_dataset.csv', date)[0]
    data = activity_dive_in_dataset('data/zone_data_6.csv', 'data/athlete_profile_dataset.csv', date)[1]


    w, h = A4
    top_margin = 2.5*cm
    bottom_margin = 2.5*cm
    left_margin = 2.5*cm
    right_margin = 2.5*cm


    # create a new PDF file
    c = canvas.Canvas(saving_name, pagesize=A4)

    # set the font and font size
    c.setFont("Helvetica", 12)

    #################################################### LOGO ###############################
    # Place the logo in the upper left corner.
    img = ImageReader("th.jpeg")
    # Get the width and height of the image.
    img_w, img_h = 50, 50
    c.drawImage(img, 0, h-img_h, width=50, height=50)

    ################################################ TITLE #################################
    # Add title
    c.setFont('Helvetica-Bold', 16)
    c.setFillColorRGB(255/255, 165/255, 0)
    title = "Activity: " + str(df_activity_visual['Date'].iloc[0]) + " - " + str(df_activity_visual['Time'].iloc[0])
    title_width = c.stringWidth(title, 'Helvetica-Bold', 16)
    c.drawCentredString(w/2, h-top_margin/2, title)

    ############################################### METRICS ##############################
    # write the move ratio
    move_ratio = round(df_activity_visual['Durée de déplacement'] / df_activity_visual['Temps écoulé'], 2)
    # Avg speed
    avg_speed = round(df_activity_visual['Vitesse moyenne'],1)
    #HRSS
    HRSS = df_activity_visual['HRSS'][0]
    HRSS_per_hour = round(HRSS / ((df_activity_visual['Durée de déplacement']/60)[0]), 1)
    #normalized power kg
    norm_power_kg = round((df_activity_visual['Puissance moyenne pondérée']/70)[0],2)

    # Convert the timestamp column to a datetime object and set it as the index
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    #rolling data
    data_rolling = data.copy()
    data_rolling.set_index('timestamp', inplace=True)
    # Resample the data to 1-minute intervals
    data_rolling = data_rolling.resample('1T').mean()
    power_20min = round(data_rolling['power'].rolling('20min').mean().max(),0)

    ####################################### PRINT METRICS ######################################
    # Calculate total width available for metrics
    total_width = w - 30 - 30
    # Calculate width per metric
    metric_width = total_width / 6

    # Draw each metric
    metrics = ['Move Ratio', 'Avg Speed', 'HRSS', 'HRSS/hour', 'Norm Power/kg', '20 min Max Power']
    values = [move_ratio[0], avg_speed[0], HRSS, HRSS_per_hour, norm_power_kg, power_20min]
    for i in range(6):
        c.setFont('Helvetica', 10)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(30 + metric_width * i, 720, metrics[i])
        c.setFont('Helvetica-Bold', 12)
        c.drawString(30 + metric_width * i, 740, str(values[i]))

    ################################### HEAR RATE ###############################################
    hr_fig = plot_hr_zones(df_activity_visual, 190)
    # Save plot as PNG file
    pio.write_image(hr_fig, 'visuals/hr_plot.png', width=1000, height=400)

    # Draw a rectangle
    c.setFillColorRGB(255/255, 216/255, 177/255) # set fill color to light orange
    c.rect(30, 650, total_width, 30, fill=True, stroke=False)

    # Add text on top of the rectangle
    c.setFont('Helvetica-Bold', 14)
    c.setFillColorRGB(0, 0, 0) # set text color to orange
    c.drawString(left_margin, 658, 'Heart Rate')

    # Draw image on canvas
    c.drawImage('visuals/hr_plot.png', x=60, y=425, width=7*inch, height=3.08*inch)

    # write the HRSS, HRSS per hour, and average HRR
    HRSS = df_activity_visual['HRSS'][0]
    HRSS_per_hour = round(HRSS / ((df_activity_visual['Durée de déplacement']/60)[0]), 2)
    HRR = round(df_activity_visual['HRR'][0]*100, 0)
    # write the TRIMP and TRIMP per hour
    trimp = df_activity_visual['trimp'][0]
    trimp_per_hour = round(trimp / ((df_activity_visual['Durée de déplacement']/60)[0]), 2)

    # Calculate the rolling mean heart rate for 20 and 60 minute windows
    hr_20min = data_rolling['heart_rate'].rolling('20min').mean().max()
    hr_60min = data_rolling['heart_rate'].rolling('60min').mean().max()

    # Calculate width per metric
    metric_width4 = total_width / 4

    #Write the HRSS, HRSS per hour, and average HRR
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30, 400, 'HRSS:')
    c.setFont('Helvetica', 10)
    c.drawString(30, 385, str(HRSS))
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30+metric_width4, 400, 'HRSS/h:')
    c.setFont('Helvetica', 10)
    c.drawString(30+metric_width4, 385, str(HRSS_per_hour))
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30+metric_width4*2, 400, 'Avg HRR:')
    c.setFont('Helvetica', 10)
    c.drawString(30+metric_width4*2, 385, str(HRR))

    # Write the TRIMP and TRIMP per hour
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30, 370, 'TRIMP:')
    c.setFont('Helvetica', 10)
    c.drawString(30, 355, str(trimp))
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30+metric_width4, 370, 'TRIMP/h:')
    c.setFont('Helvetica', 10)
    c.drawString(30+metric_width4, 355, str(trimp_per_hour))

    # Write the rolling mean heart rate for 20 and 60 minute windows
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30+metric_width4*2, 370, 'HR 20min:')
    c.setFont('Helvetica', 10)
    c.drawString(30+metric_width4*2, 355, str(round(hr_20min,0)))
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30+metric_width4*3, 370, 'HR 60min:')
    c.setFont('Helvetica', 10)
    c.drawString(30+metric_width4*3, 355, str(round(hr_60min,0)))

    ################################### SPEED ###############################################
    speed_fig = plot_speed_zones(df_activity_visual)
    # Save plot as PNG file
    pio.write_image(speed_fig, 'visuals/speed_plot.png', width=1200, height=500)

    # Draw a rectangle
    c.setFillColorRGB(175/255, 207/255, 255/255) # set fill color to light blue
    c.rect(30, 310, total_width, 30, fill=True, stroke=False)

    # Add text on top of the rectangle
    c.setFont('Helvetica-Bold', 14)
    c.setFillColorRGB(0, 0, 0) # set text color to orange
    c.drawString(left_margin, 318, 'SPEED')

    # Draw image on canvas
    c.drawImage('visuals/speed_plot.png', x=60, y=20, width=7*inch, height=3.08*inch)

    # Assuming the data is in a DataFrame called 'data' with a column 'enhanced_speed'
    speed_20min = data_rolling['enhanced_speed'].rolling('20min').mean().max()
    # Calculate standard deviation of speed
    std_speed = data['enhanced_speed'].std()
    #average speed
    speed_avg =round(df_activity_visual['Vitesse moyenne'][0], 1)

    # Calculate width per metric
    metric_width = total_width / 3

    # Draw each metric
    metrics = ['Best 20min Speed', 'Avg Speed', 'Speed Stdv']
    values = [round(speed_20min,1), speed_avg, round(std_speed,1)]
    for i in range(3):
        c.setFont('Helvetica-Bold', 12)
        c.drawString(40 + metric_width * i, 280, metrics[i])
        c.setFont('Helvetica', 10)
        c.drawString(40 + metric_width * i, 265, str(values[i])+'km/h')


    ################################################################# NEW PAGE #######################################################################
    # Start a new page
    c.showPage()

    ########################################## POWER ##########################################
    power_fig = plot_power_zones(df_activity_visual)
    # Save plot as PNG file
    pio.write_image(power_fig, 'visuals/power_plot.png', width=1200, height=500)

    # Draw a rectangle
    c.setFillColorRGB(230/255, 230/255, 230/255) # set fill color to light grey
    c.rect(30, 790, total_width, 30, fill=True, stroke=False)

    # Add text on top of the rectangle
    c.setFont('Helvetica-Bold', 14)
    c.setFillColorRGB(0, 0, 0) # set text color to orange
    c.drawString(left_margin, 798, 'Power')

    # Draw image on canvas
    c.drawImage('visuals/power_plot.png', x=60, y=530, width=7*inch, height=3.08*inch)

    # Assuming the data is in a DataFrame called 'data' with a column 'enhanced_speed'
    power_20min = round(data_rolling['power'].rolling('20min').mean().max(),0)
    #average speed
    power_avg =round(df_activity_visual['Puissance moyenne pondérée'][0], 1)
    #variability index
    var_index = round((df_activity_visual['Puissance moyenne pondérée']/df_activity_visual['Puissance moyenne'])[0],2)
    #normalized power kg
    norm_power_kg = round((df_activity_visual['Puissance moyenne pondérée']/70)[0],2)
    #Avg watts per kg
    w_kg = round((df_activity_visual['Puissance moyenne']/70)[0],2)

    metric_width3 = total_width/3

    c.setFont('Helvetica-Bold', 12)
    c.drawString(30, 500, 'Variability Index:')
    c.setFont('Helvetica', 10)
    c.drawString(30, 485, str(var_index))
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30+metric_width3, 500, 'Normalized Power:')
    c.setFont('Helvetica', 10)
    c.drawString(30+metric_width3, 485, str(power_avg)+ 'W')
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30+metric_width3*2, 500, 'Best 20min Power:')
    c.setFont('Helvetica', 10)
    c.drawString(30+metric_width3*2, 485, str(power_20min)+ ' W')

    c.setFont('Helvetica-Bold', 12)
    c.drawString(30, 470, 'Avg Watts/Kg:')
    c.setFont('Helvetica', 10)
    c.drawString(30, 455, str(w_kg)+ 'W/kg')
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30+metric_width3, 470, 'Norm Watts/Kg:')
    c.setFont('Helvetica', 10)
    c.drawString(30+metric_width3, 455, str(norm_power_kg)+ 'W/kg')

    ############################################################### POWER CURVE #########################################################################
    fig_power_curve = plot_power_curve(df_activity_visual, data)
    # Save plot as PNG file
    pio.write_image(fig_power_curve, 'visuals/power_curve.png', width=1200, height=500)

    # Draw a rectangle
    c.setFillColorRGB(200/255, 200/255, 200/255) # set fill color to light grey
    c.rect(30, 390, total_width, 30, fill=True, stroke=False)

    # Add text on top of the rectangle
    c.setFont('Helvetica-Bold', 14)
    c.setFillColorRGB(0, 0, 0) # set text color to orange
    c.drawString(left_margin, 398, 'Power Curve')

    # Draw image on canvas
    c.drawImage('visuals/power_curve.png', x=30, y=130, width=7*inch, height=3.08*inch)

    ############################################################### CADENCE ##########################################################################
    # Start a new page
    c.showPage()

    cadence_fig = plot_cadence_zones(df_activity_visual)
    # Save plot as PNG file
    pio.write_image(cadence_fig, 'visuals/cadence_plot.png', width=1200, height=700)
    
    # Draw a rectangle
    c.setFillColorRGB(102/255, 51/255, 153/255) 
    c.rect(30, 790, total_width, 30, fill=True, stroke=False)

    # Add text on top of the rectangle
    c.setFont('Helvetica-Bold', 14)
    c.setFillColorRGB(0, 0, 0) # set text color to orange
    c.drawString(left_margin, 798, 'Cadence')

    # Draw image on canvas
    c.drawImage('visuals/cadence_plot.png', x=10, y=530, width=8*inch, height=3.08*inch)

    ########################################################## GRADE ##################################################################################
    grade_fig = plot_grade_zones(df_activity_visual)
    # Save plot as PNG file
    pio.write_image(grade_fig, 'visuals/grade_plot.png', width=1200, height=700)

    # Draw a rectangle
    c.setFillColorRGB(0/255, 128/255, 0/255) 
    c.rect(30, 410, total_width, 30, fill=True, stroke=False)

    # Add text on top of the rectangle
    c.setFont('Helvetica-Bold', 14)
    c.setFillColorRGB(0, 0, 0) # set text color to orange
    c.drawString(left_margin, 418, 'Grade')

    # Draw image on canvas
    c.drawImage('visuals/grade_plot.png', x=10, y=30, width=8*inch, height=3.08*inch)

    avg_grade = round(data['grade'].mean(),0)
    # Define a downhill grade as any value below -1%
    downhill = data['grade'] < -1.5
    # Define an uphill grade as any value above 1%
    uphill = data['grade'] > 0
    # Define a flat grade as any value between -1% and 1%
    flat = (data['grade'] >= -1.5) & (data['grade'] <= 0)
    # Calculate the percentage of time spent downhill, uphill, and flat
    downhill_pct = round(100 * downhill.sum() / len(data),1)
    uphill_pct = round(100 * uphill.sum() / len(data),1)
    flat_pct = round(100 * flat.sum() / len(data),1)
    # Calculate the average speed on downhill terrain
    downhill_speed = round(data.loc[downhill, 'speed'].mean()*3.6,2)
    # Calculate the average speed on uphill terrain
    uphill_speed = round(data.loc[uphill, 'speed'].mean()*3.6,2)
    # Calculate the average speed on flat terrain
    flat_speed = round(data.loc[flat, 'speed'].mean()*3.6,2)
    #downhilltime
    downhill_time = df_activity_visual['Temps écoulé'][0] * downhill_pct / 100
    downhill_hours = int(downhill_time // 60)
    downhill_minutes = int(downhill_time % 60)
    downhill_seconds = int((downhill_time - downhill_hours * 60 - downhill_minutes) * 60)
    downhill_duration = f"{downhill_hours:02}:{downhill_minutes:02}:{downhill_seconds:02}"
    #uphill time
    uphill_time = df_activity_visual['Temps écoulé'][0] * uphill_pct / 100
    uphill_hours = int(uphill_time // 60)
    uphill_minutes = int(uphill_time % 60)
    uphill_seconds = int((uphill_time - uphill_hours * 60 - uphill_minutes) * 60)
    uphill_duration = f"{uphill_hours:02}:{uphill_minutes:02}:{uphill_seconds:02}"
    #flat time
    flat_time = df_activity_visual['Temps écoulé'][0] * flat_pct / 100
    flat_hours = int(flat_time // 60)
    flat_minutes = int(flat_time % 60)
    flat_seconds = int((flat_time - flat_hours * 60 - flat_minutes) * 60)
    flat_duration = f"{flat_hours:02}:{flat_minutes:02}:{flat_seconds:02}"
    #max uphill grade
    max_uphill_grade = round(data['grade'].max(),1)
    #max downhill grade
    max_downhill_grade = round(data['grade'].min(),1)

    c.setFont('Helvetica-Bold', 12)
    c.drawString(60, 380, "% climbing:")
    c.setFont('Helvetica', 10)
    c.drawString(60, 365, str(uphill_pct)+'%')
    c.setFont('Helvetica-Bold', 12)
    c.drawString(60+metric_width3, 380, "% flat:")
    c.setFont('Helvetica', 10)
    c.drawString(60+metric_width3, 365, str(flat_pct)+ '%')
    c.setFont('Helvetica-Bold', 12)
    c.drawString(60+metric_width3*2, 380, "% downhill:")
    c.setFont('Helvetica', 10)
    c.drawString(60+metric_width3*2, 365, str(downhill_pct)+ '%')

    c.setFont('Helvetica-Bold', 12)
    c.drawString(60, 350, "Climbing Time:")
    c.setFont('Helvetica', 10)
    c.drawString(60, 335, str(uphill_duration))
    c.setFont('Helvetica-Bold', 12)
    c.drawString(60+metric_width3, 350, "Flat Time:")
    c.setFont('Helvetica', 10)
    c.drawString(60+metric_width3, 335, str(flat_duration))
    c.setFont('Helvetica-Bold', 12)
    c.drawString(60+metric_width3*2, 350, "Downhill Time:")
    c.setFont('Helvetica', 10)
    c.drawString(60+metric_width3*2, 335, str(downhill_duration))

    c.setFont('Helvetica-Bold', 12)
    c.drawString(60, 320, "Avg Climbing Speed:")
    c.setFont('Helvetica', 10)
    c.drawString(60, 305, str(uphill_speed)+'km/h')
    c.setFont('Helvetica-Bold', 12)
    c.drawString(60+metric_width3, 320, "Avg Flat Speed:")
    c.setFont('Helvetica', 10)
    c.drawString(60+metric_width3, 305, str(flat_speed)+ 'km/h')
    c.setFont('Helvetica-Bold', 12)
    c.drawString(60+metric_width3*2, 320, "Avg Downhill Speed:")
    c.setFont('Helvetica', 10)
    c.drawString(60+metric_width3*2, 305, str(downhill_speed)+ 'km/h')

    c.setFont('Helvetica-Bold', 12)
    c.drawString(60, 290, "Avg Grade:")
    c.setFont('Helvetica', 10)
    c.drawString(60, 275, str(avg_grade)+'%')
    c.setFont('Helvetica-Bold', 12)
    c.drawString(60+metric_width3, 290, "Max Uphill Grade:")
    c.setFont('Helvetica', 10)
    c.drawString(60+metric_width3, 275, str(max_uphill_grade)+ '%')
    c.setFont('Helvetica-Bold', 12)
    c.drawString(60+metric_width3*2, 290, "Max Downhill Grade:")
    c.setFont('Helvetica', 10)
    c.drawString(60+metric_width3*2, 275, str(max_downhill_grade)+ '%')


    ############################################################### ELEVATION ##########################################################################
    elevation_fig = plot_elevation_zones(df_activity_visual)
    # Save plot as PNG file
    pio.write_image(elevation_fig, 'visuals/elevation_plot.png', width=1200, height=500)

    elevation_profile_fig = plot_elevation_profile(data)
    # Save plot as PNG file
    pio.write_image(elevation_profile_fig, 'visuals/elevation_profile_plot.png', width=1200, height=400)
            
    # Start a new page
    c.showPage()

    # Draw a rectangle
    c.setFillColorRGB(205/255, 200/255, 0/255) 
    c.rect(30, 790, total_width, 30, fill=True, stroke=False)

    # Add text on top of the rectangle
    c.setFont('Helvetica-Bold', 14)
    c.setFillColorRGB(0, 0, 0) # set text color to orange
    c.drawString(left_margin, 798, 'Elevation')

    # Draw image on canvas
    c.drawImage('visuals/elevation_plot.png', x=10, y=530, width=8*inch, height=3.08*inch)

    #metrics
    avg_elevation = round(data['altitude'].mean(),0)
    ascent = data['ascent'].max()
    descent = data['descent'].max()

    c.setFont('Helvetica-Bold', 12)
    c.drawString(30, 500, 'Average Elevation:')
    c.setFont('Helvetica', 10)
    c.drawString(30, 485, str(avg_elevation)+'m')
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30+metric_width3, 500, 'Ascent:')
    c.setFont('Helvetica', 10)
    c.drawString(30+metric_width3, 485, str(ascent)+ 'm')
    c.setFont('Helvetica-Bold', 12)
    c.drawString(30+metric_width3*2, 500, 'Descent:')
    c.setFont('Helvetica', 10)
    c.drawString(30+metric_width3*2, 485, str(descent)+ ' m')

    # Draw image on canvas
    c.drawImage('visuals/elevation_profile_plot.png', x=10, y=230, width=8*inch, height=3.08*inch)

    # save the
    c.save()