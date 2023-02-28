import pandas as pd
import os
from tqdm import tqdm

import gpxpy 
from fit2gpx import Converter, StravaConverter
import fitdecode

from garmin_fit_sdk import Decoder, Stream
from garmin_fit_sdk import Decoder, Stream
import fitparse

from tcxreader.tcxreader import TCXReader, TCXTrackPoint

################################################################### UNZIP STRAVA BULK DATA EXPORTED ##################################################################
def unzip_strava_export(dir_in):
    """
    Unzips Strava bulk export files in the specified directory.

    Parameters:
        dir_in (str): The path to the central unzipped Strava bulk export folder.

    Returns:
        None
    """
    # Step 1: Create StravaConverter object
    # - Note: the dir_in must be the path to the central unzipped Strava bulk export folder
    # - Note: You can specify the dir_out if you wish. By default it is set to 'activities_gpx', which will be created in main Strava folder specified.
    strava_conv = StravaConverter(dir_in=dir_in)

    # Step 2: Unzip the zipped files
    strava_conv.unzip_activities()

################################################################### CONVERT .GPX FILES TO .CSV ##################################################################
def read_gpx_files_indiv(directory):
    """
    Read .gpx files from a directory and save them as .csv files in a subdirectory.

    Parameters:
    -----------
    directory : str
        Path to the directory containing the .gpx files.

    Returns:
    --------
    None
    """
    output_dir = "data/activities_csv/"
    os.makedirs(output_dir, exist_ok=True)
    # loop over all files in the directory
    for file in tqdm(os.listdir(directory)):
        if file.endswith('.gpx'):
            # read the .gpx file using gpxpy library
            filepath = os.path.join(directory, file)
            with open(filepath, 'r') as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                data = [{'latitude': p.latitude,
                         'longitude': p.longitude,
                         'elevation': p.elevation,
                         'time': p.time} for p in gpx.tracks[0].segments[0].points]
            df = pd.DataFrame(data)
            # add an 'activity_id' column based on the filename
            activity_id = os.path.splitext(file)[0]
            df.insert(0, 'activity_id', activity_id)
            # Save the DataFrame as a CSV file in the output directory
            csv_file = os.path.splitext(file)[0] + '.csv'
            csv_path = os.path.join(output_dir, csv_file)
            df.to_csv(csv_path, index=False)

    print('Done')

################################################################### CONVERT .FIT FILES TO .CSV ##################################################################
def read_fit_files(directory):
    """
    Read .fit files from a directory and save them as .csv files in the 'activities_csv' folder.
    Ignore the files raising errors.

    Parameters:
    -----------
    directory : str
        Path to the directory containing the .fit files.

    Returns:
    --------
    None
    """
    # Load the activities CSV file
    activities_csv_path = 'data/activities.csv'
    df_activities = pd.read_csv(activities_csv_path)

    # Create 'activities_csv' directory if it doesn't exist
    output_directory = "data/activities_csv/"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # loop over all files in the directory
    for i, file in tqdm(enumerate(os.listdir(directory))):
        # check if the file is a .fit file
        if file.endswith('.fit'):
            # check if a corresponding CSV file exists
            csv_file = os.path.splitext(file)[0] + '.csv'
            if os.path.exists(os.path.join(output_directory, csv_file)):
                continue
            
            # read the .fit file using fitdecode
            filepath = os.path.join(directory, file)
            try:
                with fitdecode.FitReader(filepath) as fit:
                    data = []
                    for frame in fit:
                        if isinstance(frame, fitdecode.FitDataMessage):
                            if frame.name == 'record':
                                record_data = {}
                                for field in frame:
                                    try:
                                        record_data[field.name.lower()] = field.value
                                    except TypeError:
                                        pass
                                data.append(record_data)
                # Convert the data to a DataFrame
                df = pd.DataFrame(data)

                # Get the activity id from the activities CSV file
                filename = os.path.splitext(file)[0]
                df_activities_na = df_activities.dropna(subset=['Nom du fichier'])
                match = df_activities_na.loc[df_activities_na['Nom du fichier'].str.contains(filename)]
                if match.empty:
                    activity_id = None
                else:
                    activity_id = match["ID de l'activité"].values[0]

                # Add the activity id to the DataFrame
                df.insert(0, 'activity_id', activity_id)

                # Save the DataFrame as a CSV file
                csv_path = os.path.join(output_directory, csv_file)
                df.to_csv(csv_path, index=False)
                
            except TypeError:
                print(f"{file} has an issue with TypeError, moving on to the next file")
                continue
            
            except fitdecode.exceptions.FitHeaderError:
                print(f"{file} has an issue with FitHeaderError, moving on to the next file")
                continue

    print('Done')


################################################################### CONVERT .TCX FILES TO .CSV ##################################################################
def remove_first_10_chars_from_tcx_files(directory_path):
    """
    Removes the first 10 characters from all .tcx files in the specified directory.
    
    Args:
        directory_path (str): Path to the directory containing the .tcx files.
    """
    for filename in os.listdir(directory_path):
        if filename.endswith('.tcx'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r') as f:
                content = f.read()
            with open(file_path, 'w') as f:
                f.write(content[10:])


def convert_tcx_to_csv_with_activity_id(tcx_directory, activities_file, csv_directory):
    """
    Reads TCX files from a given directory, extracts data and appends the activity id, and saves the data as CSV file
    for each activity in the directory.
    
    :param tcx_directory: Directory containing TCX files
    :param activities_file: CSV file containing activity data
    :param csv_directory: Directory to save CSV files
    """
    
    # Load activities file
    df_activities = pd.read_csv(activities_file)
    
    # Iterate over TCX files in directory
    for file_name in os.listdir(tcx_directory):
        if file_name.endswith(".tcx"):
            # Create file path
            file_location = os.path.join(tcx_directory, file_name)
            
            # Read data from TCX file
            tcx_reader = TCXReader()
            data = tcx_reader.read(file_location)

            # Extract data to DataFrame
            df = pd.DataFrame({
                "time": [tp.time for tp in data.trackpoints],
                "latitude": [tp.latitude for tp in data.trackpoints],
                "longitude": [tp.longitude for tp in data.trackpoints],
                "altitude_meters": [tp.elevation for tp in data.trackpoints],
                "distance_meters": [tp.distance for tp in data.trackpoints],
                "heart_rate_bpm": [tp.hr_value for tp in data.trackpoints],
                "cadence_rpm": [tp.cadence for tp in data.trackpoints],
                "speed_mps": [tp.tpx_ext.get('Speed', None) for tp in data.trackpoints]
            })

            # Get activity id
            filename = file_name.replace(".gz", "")
            df_activities_na = df_activities.dropna(subset=['Nom du fichier'])
            match = df_activities_na.loc[df_activities_na["Nom du fichier"].str.contains(filename)]
            activity_id = match["ID de l'activité"].values[0]

            # Append activity id to DataFrame
            df["activity_id"] = activity_id

            # Save DataFrame to CSV file
            csv_filename = file_name.replace(".tcx", ".csv")
            csv_location = os.path.join(csv_directory, csv_filename)
            df.to_csv(csv_location, index=False)
