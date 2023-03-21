import gpxpy
import gpxpy.gpx
import pandas as pd
import matplotlib.pyplot as plt
import gmplot
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_report(file_name):
    # Ouvrir le fichier GPX
    with open(file_name, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    
    # Créer une liste des points de latitude et longitude
    lats = []
    longs = []
    elevations = []
    distances = []
    prev_point = None
    total_distance = 0
    
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                lats.append(point.latitude)
                longs.append(point.longitude)
                elevations.append(point.elevation)
                if prev_point is not None:
                    distance = point.distance_2d(prev_point)
                    total_distance += distance
                    distances.append(total_distance/1000) # en km
                else:
                    distances.append(0)
                prev_point = point


    #print(len(time))
    print(len(lats))
    print(len(longs))
    print(len(elevations))
    print(len(distances))
    
    # Créer une série Pandas avec les données
    df = pd.DataFrame({'distance': distances, 'elevation': elevations})
    
    # Créer un graphique de la courbe du dénivelé
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(df['distance'], df['elevation'])
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Elevation (m)')
    ax.set_title('Courbe du dénivelé en fonction de la distance')
    
    # Sauvegarder le graphique dans un fichier temporaire
    fig.savefig('elevation.png')
    
    # Créer un histogramme du nombre de kilomètres par pourcentage de dénivelé
    bins = list(range(-200, 200, 10))
    df['grade'] = df['elevation'].diff() / df['distance'].diff() * 100
    df['grade_bin'] = pd.cut(df['grade'], bins=bins)
    counts = df['grade_bin'].value_counts()
    counts = counts / counts.sum() * 100
    fig, ax = plt.subplots(figsize=(8, 6))
    counts.plot(kind='bar')
    ax.set_xlabel('Pourcentage de dénivelé')
    ax.set_ylabel('% de distance parcourue')
    ax.set_title('Pourcentage de distance parcourue par pourcentage de dénivelé')
    
    # Sauvegarder le graphique dans un fichier temporaire
    fig.savefig('grade.png')
    
    # Créer une carte avec la trace de la course
    gmap = gmplot.GoogleMapPlotter(lats[0], longs[0], 13)
    gmap.plot(lats, longs)
    gmap.draw('map.html')


    """     # Créer un graphique de la distance parcourue
    # Créer une liste des portions de la trace au-dessus de 10% de dénivelé
    high_grade_segments = []
    segment_start = None
    
    for i, row in df.iterrows():
        if row['grade'] >= 10 and segment_start is None:
            segment_start = i
        elif row['grade'] < 10 and segment_start is not None:
            high_grade_segments.append((segment_start, i))
            segment_start = None
    
    if segment_start is not None:
        high_grade_segments.append((segment_start, len(df))) """
    """
    # Créer un graphique avec les portions de la trace au-dessus de 10% de dénivelé
    fig, ax = plt.subplots(figsize=(8, 6))
    for start, end in high_grade_segments:
        ax.plot(df.loc[start:end, 'distance'], df.loc[start:end, 'elevation'])
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Elevation (m)')
    ax.set_title("Portions de la trace au-dessus de 10% de dénivelé")
    
    # Sauvegarder le graphique dans un fichier temporaire
    fig.savefig('high_grade.png')   """
    
    # Calculer les statistiques
    total_distance = df['distance'].max()
    total_elevation_gain = df['elevation'].diff().clip(lower=0).sum()
    total_elevation_loss = df['elevation'].diff().clip(upper=0).sum()
    above_altitude_count = (df['elevation'] >= 1000).sum()
    start_lat = lats[0]
    start_long = longs[0]
    end_lat = lats[-1]
    end_long = longs[-1]
    time_hours = total_distance / 20



    """
      # Extraire les portions de la trace au-dessus de 10% de dénivelé
    steep = df[df['grade'] > 10]
    steep['diff'] = steep['elevation'].diff()
    steep['start_lat'] = lats[:-1]
    steep['start_long'] = longs[:-1]
    steep['end_lat'] = lats[1:]
    steep['end_long'] = longs[1:]
    
    # Créer une carte avec les portions de la trace au-dessus de 10% de dénivelé
    gmap = gmplot.GoogleMapPlotter(lats[0], longs[0], 13)
    for i, row in steep.iterrows():
        gmap.plot([row['start_lat'], row['end_lat']], [row['start_long'], row['end_long']])
    gmap.draw('steep.html')
    

    """


    # Calculer les statistiques
    total_distance = df['distance'].iloc[-1]
    total_elevation_gain = df['elevation'].diff().clip(lower=0).sum()
    total_elevation_loss = df['elevation'].diff().clip(upper=0).sum()
    altitude_threshold = 1000 # en mètres
    distance_above_threshold = df[df['elevation'] > altitude_threshold]['distance'].iloc[-1]
    start_lat = lats[0]
    start_long = longs[0]
    end_lat = lats[-1]
    end_long = longs[-1]
    time_to_finish = total_distance / 20 * 60 # en minutes
    
    # Créer un PDF avec les graphiques et les statistiques
    pdf_file = f"{file_name.split('.')[0]}.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    c.setFont('Helvetica', 12)
    c.drawString(100, 700, 'Briefing développé par Joseph Mestrallet')
    c.drawString(100, 650, f"Distance totale : {total_distance:.2f} km")
    c.drawString(100, 630, f"Dénivelé positif total : {total_elevation_gain:.2f} m")
    c.drawString(100, 610, f"Dénivelé négatif total : {total_elevation_loss:.2f} m")
    c.drawString(100, 590, f"Distance audessus de {altitude_threshold} m : {distance_above_threshold:.2f} km")
    c.drawString(100, 570, f"Distance entre le point de départ et le point d'arrivée : {total_distance:.2f} km")
    c.drawString(100, 550, f"Temps estimé à 20 km/h : {time_to_finish:.2f} minutes")
    c.drawImage('elevation.png', 50, 400, width=500, height=300)
    c.drawImage('grade.png', 50, 100, width=500, height=300)
    c.showPage()
    c.drawImage('map.png', 50, 400, width=500, height=300)
    c.drawImage('steep.png', 50, 100, width=500, height=300)
    c.save()
    
    return pdf_file


generate_report("eco.gpx")
