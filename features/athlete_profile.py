import pandas as pd
import numpy as np
import math 


######################################### HEART RATE ZONES ##########################################################

def calculate_hr_zones_hrmax(hrmax):
    """
    Calculates heart rate zones using the percentage of HRmax method.

    Args:
        hrmax (int): Maximum heart rate.

    Returns:
        pandas.DataFrame: Heart rate zones, including zone number, zone name,
                           and heart rate range for each zone.
    """

    zone_ranges = [0.5, 0.6, 0.7, 0.8, 0.9]
    zone_names = ['Endurance', 'Moderate', 'Tempo', 'Threshold', 'Anaerobic']
    hr_zones = []
    for i, zone_range in enumerate(zone_ranges):
        lower_range = zone_ranges[i] * hrmax
        upper_range = zone_ranges[i+1] * hrmax if i+1 < len(zone_ranges) else float("inf")
        if i == 0:
            hr_range = f'< {upper_range}'
        elif i == 4:
            hr_range = f'>{lower_range}'
        else:
            hr_range = f'{lower_range:.0f} - {upper_range:.0f}'
        hr_zones.append((i+1, zone_names[i], lower_range, upper_range, hr_range))
    zones_df = pd.DataFrame(hr_zones, columns=['Zone', 'Name', 'Lower Bound', 'Upper Bound', 'Range'])

    return zones_df


############################################## INTENSITY SCORE #######################################################

def intensity_score(df, power_col, ftp):
    """
    Add the intensity score column to an existing df based on the athlete ftp, which is the ratio of the Normalized Power to FTP.

    Args:
        df: input dataframe.
        ftp (int): athlete ftp.

    Returns:
        pandas.DataFrame: new df with intensity score column.
    """
    df['intensity_score'] = round(df[power_col] * 100 / ftp, 2)

    return df

############################################# TIME IN HEART RATE ZONES ###############################################

def calculate_time_in_zones(df, hr_data):
    """
    Calculate the time spent in each heart rate zone for each activity and add the results as columns.
    
    Args:
    - df (pandas.DataFrame): A DataFrame containing information about each activity.
    - hr_data (pandas.DataFrame): A DataFrame containing the heart rate zones and corresponding upper and lower bounds.
    
    Returns:
    - df (pandas.DataFrame): The original DataFrame with new columns for the time spent in each heart rate zone.
    """
        
    # Loop through the rows in df and calculate time spent in each zone for the corresponding activity
    for index, row in df.iterrows():    
    # Extract activity id from the file name column
        activity_num = str(row["Nom du fichier"]).split("/")[-1].split(".")[0]
        # Load the activity data
        activity_file = f"data/activities_csv/{activity_num}.csv"
        csv_data = pd.read_csv(activity_file)
        csv_data = csv_data[['timestamp', 'heart_rate']]

        # Calculate the time spent in each zone
        for index_2, row_2 in csv_data.iterrows():
            if row_2["heart_rate"] < hr_data["Upper Bound"].iloc[0]:
                csv_data.loc[index_2, "Zone"] = hr_data["Zone"].iloc[0]
            elif hr_data["Lower Bound"].iloc[1] < row_2["heart_rate"] < hr_data["Upper Bound"].iloc[1]:
                csv_data.loc[index_2, "Zone"] = hr_data["Zone"].iloc[1]
            elif hr_data["Lower Bound"].iloc[2] < row_2["heart_rate"] < hr_data["Upper Bound"].iloc[2]:
                csv_data.loc[index_2, "Zone"] = hr_data["Zone"].iloc[2]
            elif hr_data["Lower Bound"].iloc[3] < row_2["heart_rate"] < hr_data["Upper Bound"].iloc[3]:
                csv_data.loc[index_2, "Zone"] = hr_data["Zone"].iloc[3]
            elif row_2["heart_rate"] > hr_data["Lower Bound"].iloc[4]:
                csv_data.loc[index_2, "Zone"] = hr_data["Zone"].iloc[4]

        # Group by zone and calculate the percentage of time spent in each zone
        csv_grouped = csv_data.groupby("Zone")["timestamp"].count().reset_index()
        csv_grouped = csv_grouped.rename(columns={"timestamp": "Count"})
        csv_grouped['perc'] = round(csv_grouped['Count'] / len(csv_data), 2)

        # Add new columns with time spent in each zone to df
        try:
            df.loc[index, "time_z1"] = csv_grouped[csv_grouped["Zone"] == 1]["perc"].values[0]
        except IndexError:
            df.loc[index, "time_z1"] = 0
        try:
            df.loc[index, "time_z2"] = csv_grouped[csv_grouped["Zone"] == 2]["perc"].values[0]
        except IndexError:
            df.loc[index, "time_z2"] = 0
        try:
            df.loc[index, "time_z3"] = csv_grouped[csv_grouped["Zone"] == 3]["perc"].values[0]
        except IndexError:
            df.loc[index, "time_z3"] = 0
        try:
            df.loc[index, "time_z4"] = csv_grouped[csv_grouped["Zone"] == 4]["perc"].values[0]
        except IndexError:
            df.loc[index, "time_z4"] = 0
        try:
            df.loc[index, "time_z5"] = csv_grouped[csv_grouped["Zone"] == 5]["perc"].values[0]
        except IndexError:
            df.loc[index, "time_z5"] = 0
    
    return df

############################################### RELATIVE EFFORT (TRIMP) #####################################################

def relative_effort_measure(df, time_z1 = 'time_z1', time_z2 = 'time_z2', time_z3 = 'time_z3', time_z4 = 'time_z4', time_z5 = 'time_z5', activity_time='Durée de déplacement'):
    """
    Calculate the relative effort for each activity and add the results as columns, which is a measure 
    that considers the intensity and duration of the workout
    
    Args:
    - df (pandas.DataFrame): A DataFrame containing information about each activity.
    - time_z1: column corresponding to the percentage of time spent in z1
    - time_z2: column corresponding to the percentage of time spent in z2
    - time_z3: column corresponding to the percentage of time spent in z3
    - time_z4: column corresponding to the percentage of time spent in z4
    - time_z5: column corresponding to the percentage of time spent in z5
    - activity_time: column with the activity length
    
    Returns:
    - df (pandas.DataFrame): The original DataFrame with new columns for the intensity score.
    """

    df['TRIMP'] = df[time_z1]*100 + df[time_z2]*200 + df[time_z3]*300 + df[time_z4]*400 +  df[time_z5]*500
    df['TRIMP_score'] = round((df['TRIMP'] / df['TRIMP'].max())*100, 2)
    df['Relative Effort'] = df['TRIMP_score']*(df[activity_time]/60)

    return df

############################################## TRAINING LOAD (TSS) #######################################################

def training_load_measure(df, ftp, activity_time='Durée de déplacement', power='Puissance moyenne pondérée', ints='intensity_score'):
    """
    Calculate the TSS for each activity and add the results as columns, which is is 
    calculated using a combination of power output and heart rate data
    
    Args:
    - df (pandas.DataFrame): A DataFrame containing information about each activity.
    - ftp: athlete ftp.
    - activity_time: column with the activity length
    - power: columnwith the ride power
    - ints: column with the intensity score
    
    Returns:
    - df (pandas.DataFrame): The original DataFrame with new columns for the TSS score.
    """

    df["TSS"] = ((df[activity_time]*60)*df[power]*df[ints]) / (ftp*3600)

    return df



