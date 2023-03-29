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

    zone_ranges = [0.50, 0.585, 0.7772, 0.87, 0.9689]
    zone_names = ['Endurance', 'Moderate', 'Tempo', 'Threshold', 'Anaerobic']
    hr_zones = []
    for i, zone_range in enumerate(zone_ranges):
        lower_range = zone_ranges[i] * hrmax
        upper_range = zone_ranges[i+1] * hrmax if i+1 < len(zone_ranges) else float("inf")
        if i == 0:
            hr_range = f'< {upper_range:.0f}'
        elif i == 4:
            hr_range = f'>{lower_range:.0f}'
        else:
            hr_range = f'{lower_range:.0f} - {upper_range:.0f}'
        hr_zones.append((i+1, zone_names[i], lower_range, upper_range, hr_range))
    zones_df = pd.DataFrame(hr_zones, columns=['Zone', 'Name', 'Lower Bound', 'Upper Bound', 'Range'])

    return zones_df

def calculate_hr_zones_RE(hrmax):
    """
    Calculates heart rate zones using the percentage of HRmax method based on Strava findings

    Args:
        hrmax (int): Maximum heart rate.

    Returns:
        pandas.DataFrame: Heart rate zones, including zone number, zone name,
                           and heart rate range for each zone.
    """

    zone_ranges = [0.50, 0.585, 0.6811, 0.7772, 0.87, 0.91945, 0.9689]
    zone_names = ['Endurance', 'Moderate', 'Inter1', 'Tempo', 'Inter2', 'Threshold', 'Anaerobic']
    hr_zones = []
    for i, zone_range in enumerate(zone_ranges):
        lower_range = zone_ranges[i] * hrmax
        upper_range = zone_ranges[i+1] * hrmax if i+1 < len(zone_ranges) else float("inf")
        if i == 0:
            hr_range = f'< {upper_range:.0f}'
        elif i == 6:
            hr_range = f'>{lower_range:.0f}'
        else:
            hr_range = f'{lower_range:.0f} - {upper_range:.0f}'
        hr_zones.append((i+1, zone_names[i], round(lower_range,0), round(upper_range,0), hr_range))
    zones_df = pd.DataFrame(hr_zones, columns=['Zone', 'Name', 'Lower Bound', 'Upper Bound', 'Range'])

    return zones_df

def calculate_hr_zones_elevate(hrmax):
    """
    Calculates heart rate zones using the percentage of HRmax method based on Strava findings

    Args:
        hrmax (int): Maximum heart rate.

    Returns:
        pandas.DataFrame: Heart rate zones, including zone number, zone name,
                           and heart rate range for each zone.
    """

    zone_ranges = [0.50, 0.6, 0.7, 0.8, 0.9, 1.0]
    zone_names = ['Endurance', 'Moderate', 'Tempo', 'Threshold', 'Anaerobic', 'Max']
    hr_zones = []
    for i, zone_range in enumerate(zone_ranges):
        lower_range = zone_ranges[i] * hrmax
        upper_range = zone_ranges[i+1] * hrmax if i+1 < len(zone_ranges) else float("inf")
        if i == 0:
            hr_range = f'< {upper_range:.0f}'
        elif i == 5:
            hr_range = f'>{lower_range:.0f}'
        else:
            hr_range = f'{lower_range:.0f} - {upper_range:.0f}'
        hr_zones.append((i+1, zone_names[i], round(lower_range,0), round(upper_range,0), hr_range))
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
    df['intensity_score'] = round(df[power_col] * 100 / ftp, 0)

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
        if "Nom du fichier" in row:
            activity_num = str(row["Nom du fichier"]).split("/")[-1].split(".")[0]
            # Load the activity data
            activity_file = f"data/activities_csv/{activity_num}.csv"
        else:
            activity_num = row['nom']
            activity_file = f"data/strava_test_csv/{activity_num}.csv"
            
        csv_data = pd.read_csv(activity_file)
        # Check if the original column names exist
        if 'timestamp' in csv_data.columns and 'heart_rate' in csv_data.columns:
            csv_data = csv_data[['timestamp', 'heart_rate']]
        else:
            # Use alternative column names
            csv_data = csv_data[['time', 'heart_rate_bpm']]
            csv_data = csv_data.rename(columns={'time': 'timestamp', 'heart_rate_bpm': 'heart_rate'})

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
        csv_grouped = csv_grouped = csv_data.groupby("Zone").agg({'timestamp':'count', 'heart_rate':'mean'}).rename(columns={"timestamp": "Count", "heart_rate": 'avg_HR'}).reset_index()
        csv_grouped['perc'] = round(csv_grouped['Count'] / len(csv_data), 2)
        

        # Add new columns with time spent in each zone to df
        try:
            df.loc[index, "time_z1"] = csv_grouped[csv_grouped["Zone"] == 1]["perc"].values[0]
            df.loc[index, "avgHR_z1"] = csv_grouped[csv_grouped["Zone"] == 1]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z1"] = 0
            df.loc[index, "avgHR_z1"] = 0
        try:
            df.loc[index, "time_z2"] = csv_grouped[csv_grouped["Zone"] == 2]["perc"].values[0]
            df.loc[index, "avgHR_z2"] = csv_grouped[csv_grouped["Zone"] == 2]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z2"] = 0
            df.loc[index, "avgHR_z2"] = 0
        try:
            df.loc[index, "time_z3"] = csv_grouped[csv_grouped["Zone"] == 3]["perc"].values[0]
            df.loc[index, "avgHR_z3"] = csv_grouped[csv_grouped["Zone"] == 3]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z3"] = 0
            df.loc[index, "avgHR_z3"] = 0
        try:
            df.loc[index, "time_z4"] = csv_grouped[csv_grouped["Zone"] == 4]["perc"].values[0]
            df.loc[index, "avgHR_z4"] = csv_grouped[csv_grouped["Zone"] == 4]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z4"] = 0
            df.loc[index, "avgHR_z4"] = 0
        try:
            df.loc[index, "time_z5"] = csv_grouped[csv_grouped["Zone"] == 5]["perc"].values[0]
            df.loc[index, "avgHR_z5"] = csv_grouped[csv_grouped["Zone"] == 5]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z5"] = 0
            df.loc[index, "avgHR_z5"] = 0
    
    return df

def calculate_time_in_zones_RE(df, hr_data):
    """
    Calculate the time spent in each heart rate zone for each activity and add the results as columns, useful for Coggan Model
    
    Args:
    - df (pandas.DataFrame): A DataFrame containing information about each activity.
    - hr_data (pandas.DataFrame): A DataFrame containing the heart rate zones and corresponding upper and lower bounds.
    
    Returns:
    - df (pandas.DataFrame): The original DataFrame with new columns for the time spent in each heart rate zone.
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
            activity_file = f"data/strava_test_csv/{activity_num}.csv"
            
        csv_data = pd.read_csv(activity_file)
        # Check if the original column names exist
        if 'timestamp' in csv_data.columns and 'heart_rate' in csv_data.columns:
            csv_data = csv_data[['timestamp', 'heart_rate']]
        else:
            # Use alternative column names
            csv_data = csv_data[['time', 'heart_rate_bpm']]
            csv_data = csv_data.rename(columns={'time': 'timestamp', 'heart_rate_bpm': 'heart_rate'})

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
            elif hr_data["Lower Bound"].iloc[4] < row_2["heart_rate"] < hr_data["Upper Bound"].iloc[4]:
                csv_data.loc[index_2, "Zone"] = hr_data["Zone"].iloc[4]
            elif hr_data["Lower Bound"].iloc[5] < row_2["heart_rate"] < hr_data["Upper Bound"].iloc[5]:
                csv_data.loc[index_2, "Zone"] = hr_data["Zone"].iloc[5]
            elif row_2["heart_rate"] > hr_data["Lower Bound"].iloc[6]:
                csv_data.loc[index_2, "Zone"] = hr_data["Zone"].iloc[6]

        # Group by zone and calculate the percentage of time spent in each zone
        csv_grouped = csv_grouped = csv_data.groupby("Zone").agg({'timestamp':'count', 'heart_rate':'mean'}).rename(columns={"timestamp": "Count", "heart_rate": 'avg_HR'}).reset_index()
        csv_grouped['perc'] = round(csv_grouped['Count'] / len(csv_data), 2)
        

        # Add new columns with time spent in each zone to df
        try:
            df.loc[index, "time_z1"] = csv_grouped[csv_grouped["Zone"] == 1]["perc"].values[0]
            df.loc[index, "avgHR_z1"] = csv_grouped[csv_grouped["Zone"] == 1]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z1"] = 0
            df.loc[index, "avgHR_z1"] = 0
        try:
            df.loc[index, "time_z2"] = csv_grouped[csv_grouped["Zone"] == 2]["perc"].values[0]
            df.loc[index, "avgHR_z2"] = csv_grouped[csv_grouped["Zone"] == 2]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z2"] = 0
            df.loc[index, "avgHR_z2"] = 0
        try:
            df.loc[index, "time_z3"] = csv_grouped[csv_grouped["Zone"] == 3]["perc"].values[0]
            df.loc[index, "avgHR_z3"] = csv_grouped[csv_grouped["Zone"] == 3]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z3"] = 0
            df.loc[index, "avgHR_z3"] = 0
        try:
            df.loc[index, "time_z4"] = csv_grouped[csv_grouped["Zone"] == 4]["perc"].values[0]
            df.loc[index, "avgHR_z4"] = csv_grouped[csv_grouped["Zone"] == 4]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z4"] = 0
            df.loc[index, "avgHR_z4"] = 0
        try:
            df.loc[index, "time_z5"] = csv_grouped[csv_grouped["Zone"] == 5]["perc"].values[0]
            df.loc[index, "avgHR_z5"] = csv_grouped[csv_grouped["Zone"] == 5]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z5"] = 0
            df.loc[index, "avgHR_z5"] = 0
        try:
            df.loc[index, "time_z6"] = csv_grouped[csv_grouped["Zone"] == 6]["perc"].values[0]
            df.loc[index, "avgHR_z6"] = csv_grouped[csv_grouped["Zone"] == 6]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z6"] = 0
            df.loc[index, "avgHR_z6"] = 0
        try:
            df.loc[index, "time_z7"] = csv_grouped[csv_grouped["Zone"] == 7]["perc"].values[0]
            df.loc[index, "avgHR_z7"] = csv_grouped[csv_grouped["Zone"] == 7]["avg_HR"].values[0]
        except IndexError:
            df.loc[index, "time_z7"] = 0
            df.loc[index, "avgHR_z7"] = 0
    
    return df

############################################## RELATIVE EFFORT ############################################################

def calculate_new_relative_effort(df, a=0.15431269224351535,
                                  b=0.027420732193484548,
                                  c=0.38565644853265013,
                                  d=0.5323576919121238,
                                  e=0.6270385873082338,
                                  f=1.0517240453307226,
                                  g=1.0598455728195533):
    # define the weighting factor function
    weighting_factor = lambda x: 0.64*np.exp(1.92*x/190)

    # create a list of tuples, where each tuple contains the zone time and heart rate columns
    zone_columns = [('time_z1', 'avgHR_z1'), ('time_z2', 'avgHR_z2'), ('time_z3', 'avgHR_z3'), ('time_z4', 'avgHR_z4'), ('time_z5', 'avgHR_z5'), ('time_z6', 'avgHR_z6'), ('time_z7', 'avgHR_z7')]

    # iterate over the list of tuples and create a new column for each zone
    for i, (zone_time_col, zone_hr_col) in enumerate(zone_columns):
        # create a new column name for the duration
        duration_col_name = f'duration_HR{i+1}'
        # create a new column for the duration
        df[duration_col_name] = df['Durée de déplacement'] * df[zone_time_col]
        
        # create a new column name for the weighting factor
        wfactor_col_name = f'wfactor{i+1}'
        # apply the calculation using lambda function to create the new column
        df[wfactor_col_name] = weighting_factor(df[zone_hr_col])

        # create a new column name for the weighted duration
        weighted_duration_col_name = f'weighted_duration_HR{i+1}'
        # calculate the weighted duration
        df[weighted_duration_col_name] = df[duration_col_name] * df[zone_hr_col] / 190 * df[wfactor_col_name]
    
    # calculate the new_relative_effort column
    df['new_relative_effort'] = round((df['weighted_duration_HR1'] * a
                                 + df['weighted_duration_HR2'] * b
                                 + df['weighted_duration_HR3'] * c
                                 + df['weighted_duration_HR4'] * d
                                 + df['weighted_duration_HR5'] * e
                                 + df['weighted_duration_HR6'] * f
                                 + df['weighted_duration_HR7'] * g),0)
    df = df[['Date', 'Time', 'Nom du fichier', 'Durée de déplacement', 'Distance',
       'Fréquence cardiaque moyenne', 'Fréquence cardiaque maximum',
       'Vitesse moyenne', 'Cadence moyenne', 'Puissance moyenne',
       "Poids de l'athlète",'Puissance moyenne pondérée', "intensity_score", "Mesure d'effort", "new_relative_effort"]]
    
    return df


############################################## TRAINING LOAD (TSS) #######################################################

def training_load_measure(df, ftp=405, activity_time='Durée de déplacement', power='Puissance moyenne pondérée', ints='intensity_score'):
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

    df["TSS"] = round(((df[activity_time]*60)*df[power]*df[ints]) / (ftp*3600),0)

    return df

######################################################## HHR ########################################

def HRR(df, restingHR=65, maxHR=190, HRavg = 'Fréquence cardiaque moyenne'):
    """
    Add the Heart Rate Reserve score column to an existing df based on the athlete resting HR, max HR, and activity average HR.

    Args:
        df: input dataframe.
        restingHR (int): athlete resting Heart Rate.
        maxHR (int): athlete max Heart Rate.
        HRavg (int): athlete average Heart Rate during activity.

    Returns:
        pandas.DataFrame: new df with HRR metric column.
    """
    df[HRavg] = df[HRavg].astype(float)
    restingHR = int(restingHR)
    maxHR = int(maxHR)
    a = df[HRavg] - restingHR
    b = maxHR-restingHR
    df['HRR'] = a / b

    return df

######################################################## TRIMP ########################################

def trimp(df, duration='Durée de déplacement', HRR='HRR'):
    """
    Add the TRIMP column to an existing df based on the athlete resting HR, max HR, and activity average HR.

    Args:
        df: input dataframe.
        duration (int): activity duration in minutes.
        HRR: activity Heart rate Researved 

    Returns:
        pandas.DataFrame: new df with trimp column.
    """
    df['trimp'] = round(df[duration]*df[HRR]*0.64*np.exp(1.92*df[HRR]), 0)

    return df


######################################################## HRSS ########################################

def HRSS(df, lthr=172, HRrest=65, HHRmax=190, trimp='trimp'):
    """
    Add the Heart Rate Stress Score column to an existing df based on the activity duration, the athlete HRR, and the athlete LTHR.

    Args:
        df: input dataframe.
        lthr (int): athlete Lactate Threshold Heart Rate.
        HRrest (int): athlete resting Heart Rate.
        HRmax (int): athlete max Heart Rate.
        trimp: (int)  activity trimp.

    Returns:
        pandas.DataFrame: new df with HRSS score column.
    """
    HRR_LTHR= (lthr-HRrest)/(HHRmax-HRrest)
    hour_trimp_lthr = 60*HRR_LTHR*0.64*np.exp(1.92*HRR_LTHR)
    df['HRSS'] = round((df[trimp]/(hour_trimp_lthr))*100, 0)

    return df

######################################################## FITNESS ########################################

import pandas as pd
import math

def calculate_fitness(df, hrss='HRSS', date='Date'):
    """
    Add the Fitness column to a new daily dataframe based on the date and HRSS (stress score).

    Args:
        df: input dataframe.
        hrss: HRSS column.
        date: date column.

    Returns:
        pandas.DataFrame: new df with Date and Fitness columns.
    """

    df[date] =  pd.to_datetime(df[date])

    # Get min and max dates from the input dataframe
    min_date = pd.to_datetime(df[date]).min()
    max_date = pd.to_datetime(df[date]).max()

    # Create a new dataframe with daily dates between min and max dates
    daily_df = pd.DataFrame(pd.date_range(min_date, max_date), columns=[date])

    # Initialize the fitness column with NaN values
    daily_df['Fitness'] = pd.Series([float('nan')]*len(daily_df))

    # Initialize previous_fitness as 0
    previous_fitness = 0

    # Loop through each row in the daily dataframe
    for i, row in daily_df.iterrows():
        # Get the date and HRSS for this row
        row_date = pd.to_datetime(row[date]).date()
        if row_date in pd.to_datetime(df[date]).dt.date.values:
            row_hrss = df.loc[pd.to_datetime(df[date]).dt.date == row_date, hrss].values[0]
        else:
            row_hrss = 0

        # Calculate the fitness score for this row based on the previous fitness and HRSS
        fitness = previous_fitness + (row_hrss - previous_fitness) * (1 - math.exp(-1/42))

        # Update the fitness column for this row
        daily_df.loc[i, 'Fitness'] = round(fitness, 1)
        daily_df.loc[i, 'Fitness Diff'] = round(fitness - previous_fitness, 1)

        # Update previous_fitness for the next row
        previous_fitness = fitness

    # Merge the daily_df with the original df based on the date column
    df_merged = pd.merge(df, daily_df, on=date, how='left')

    return df_merged, daily_df


########################################################## FATIGUE ##############################################

def calculate_fatigue(df, hrss='HRSS', date='Date'):
    """
    Add the Fatigue column to an existing df based on the HRSS (stress score).

    Args:
        df: input dataframe.
        hrss: (int) HRSS column.
        date: date column.

    Returns:
        pandas.DataFrame: new df with Fatigue column.
    """
    df[date] =  pd.to_datetime(df[date])

    # Get min and max dates from the input dataframe
    min_date = pd.to_datetime(df[date]).min()
    max_date = pd.to_datetime(df[date]).max()

    # Create a new dataframe with daily dates between min and max dates
    daily_df = pd.DataFrame(pd.date_range(min_date, max_date), columns=[date])

    # Initialize the Fatigue column with NaN values
    daily_df['Fatigue'] = pd.Series([float('nan')]*len(daily_df))

    # Initialize previous_fatigue as 0
    previous_fatigue = 0

    # Loop through each row in the daily dataframe
    for i, row in daily_df.iterrows():
        # Get the date and HRSS for this row
        row_date = pd.to_datetime(row[date]).date()
        if row_date in pd.to_datetime(df[date]).dt.date.values:
            row_hrss = df.loc[pd.to_datetime(df[date]).dt.date == row_date, hrss].values[0]
        else:
            row_hrss = 0

        # Calculate the fatigue score for this row based on the previous fatigue and HRSS
        fatigue = previous_fatigue + (row_hrss - previous_fatigue) * (1 - math.exp(-1/7))

        # Update the fatigue column for this row
        daily_df.loc[i, 'Fatigue'] = round(fatigue, 1)
        daily_df.loc[i, 'Fatigue Diff'] = round(fatigue - previous_fatigue, 1)

        # Update previous_fitness for the next row
        previous_fatigue = fatigue

    # Merge the daily_df with the original df based on the date column
    df_merged = pd.merge(df, daily_df, on=date, how='left')

    return df_merged, daily_df


############################################################# FORM ###########################################

def calculate_form(df, fitness='Fitness', fatigue='Fatigue', date='Date'):
    """
    Add the Form column to an existing df based on the date, fitness, and fatigue score.

    Args:
        df: input dataframe.
        fitness: fitness column.
        fatigue: fatigue column.

    Returns:
        pandas.DataFrame: new df with Form column.
    """
    
    fatigue_df = calculate_fatigue(df)[1]
    fitness_df = calculate_fitness(df)[1]

    df_merged = pd.merge(fatigue_df, fitness_df, on=date)

    # Assuming your input dataframe is named 'daily_df'
    df_merged['previous_fitness'] = df_merged['Fitness'].shift(1)
    df_merged['previous_fatigue'] = df_merged['Fatigue'].shift(1)
    df_merged['Form'] = df_merged['previous_fitness'] - df_merged['previous_fatigue']

    df_merged = df_merged[['Date', 'Form']]

    # Merge the df_merged with the original df based on the date column
    df_merged = pd.merge(df, df_merged, on=date, how='left')

    return df_merged
