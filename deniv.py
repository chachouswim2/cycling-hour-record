import gpxpy
import math
import numpy as np 
import matplotlib.pyplot as plt
distances = list(range(1, 42+1))
vent_degrees=19

# coefficients for pace adjustment per kilometer
pace_coefficients = [1.000080048, 0.9597443092, 1.025334806, 1.003949717, 0.9948160418, 1.007657106, 1.000848193,
                         1.016732615, 1.015279582, 0.9580846049, 0.9721277418, 1.03674923, 1.022787599, 0.9956628087,
                         1.013011624, 0.9886574388, 0.9879245949, 0.9798662564, 0.974054114, 0.9889179181, 0.9804454344,
                         0.9684757223, 1.025063144, 0.9979819092, 0.9931579049, 0.9969565867, 1.00270318, 1.003428238,
                         1.021951599, 1.035861001, 1.042988514, 1.041245756, 1.043822327, 1.042574641, 0.9938844916,
                         1.002471777, 0.9728768892, 0.957812918, 0.9901057078, 0.9901057078, 0.9805995192, 0.9732006846,
                         0.9726515267]







def elevation_gain_per_km2(gpx_file):
    gpx = gpxpy.parse(open(gpx_file, 'r'))
    distance, elev_gain, elev_gaintot, elev_loss, last_point, elev_profile, elev_profiled, i = 0, 0, 0, 0, None, [], [], 0

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                if last_point:
                    distance += point.distance_2d(last_point)
                    elev_gain += max(point.elevation - last_point.elevation, 0)
                    elev_loss += max(last_point.elevation - point.elevation, 0)
                last_point = point
                if math.floor(distance / 1000) >= len(elev_profile):
                    elev_profile.append(elev_gain)
                    elev_profiled.append(elev_loss)
                    elev_gaintot+=elev_gain
                    elev_gain, elev_loss, i = 0, 0, i + 1
    
    distances = list(range(1, i+1))
    elev = [x - y for x, y in zip(elev_profile, elev_profiled)]
    fig, ax = plt.subplots()
    # Ajouter une zone rouge au dessus de 0 
    
    ax.axhspan(0, 20, facecolor='lightcoral', alpha=0.5)
    ax.text(1, 15, 'Kilometres mostly uphill, hang on ', fontsize=12, color='darkgreen')


    # Ajouter une zone verte en dessous de 0
    ax.plot(distances, elev)
    ax.axhspan(-25, 0, facecolor='lightgreen', alpha=0.5)
    ax.text(5, -15, 'Kilometres mostly downhill, speed up ', fontsize=12, color='maroon')
    plt.xlabel("Distance (km)")
    plt.ylabel("Elevation (m)")
    plt.title("Elevation during the Paris marathon")
    plt.show()
    print(elev_profile)
    print(elev_profiled)
    print(len(elev_profile))
    print(len(elev_profiled))
    print(elev)
    print("l'elevation tot est : ",elev_gaintot)
    print(sum(elev_profile))






def deg_to_rad(deg):
    """Conversion d'un angle en degrés en radians."""
    return deg * math.pi / 180

def get_bearing(lat1, lon1, lat2, lon2):
    """Calcul de l'orientation en degrés entre deux points."""
    delta_lon = deg_to_rad(lon2 - lon1)
    lat1, lat2 = deg_to_rad(lat1), deg_to_rad(lat2)
    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    return (math.atan2(y, x) * 180 / math.pi + 360) % 360

def calculate_orientation(gpx_file):
    """Calcul de l'orientation de chaque kilomètre par rapport au Nord."""
    gpx = gpxpy.parse(open(gpx_file, 'r'))
    points = gpx.tracks[0].segments[0].points
    last_lat, last_lon = points[0].latitude, points[0].longitude
    orientations = []
    print(len(points))
    b=len(points)
    print(b)
    z=round(len(points)/42.194)
    for point in points[z::z]:
        orientation = get_bearing(last_lat, last_lon, point.latitude, point.longitude)
        orientations.append(int(orientation))
        last_lat, last_lon = point.latitude, point.longitude
    orientations.pop()
    return orientations
    #print(orientations)
    #print(len(orientations))
    #plt.plot(distances,orientations)
    #plt.show()





def impact_vent_liste(vent_degrees):
    # Conversion des degrés en radians
    vent_rad = math.radians(vent_degrees)
    
    # Initialisation de la liste de valeurs de retour
    valeurs = []
    direction_list_degrees=calculate_orientation("Paris2023.gpx")
    
    # Calcul de la valeur de retour pour chaque direction
    for direction_degrees in direction_list_degrees:
        direction_rad = math.radians(direction_degrees)
        diff_rad = vent_rad - direction_rad
        
        # Normalisation de l'angle entre -pi et pi
        if diff_rad > math.pi:
            diff_rad -= 2*math.pi
        elif diff_rad < -math.pi:
            diff_rad += 2*math.pi
            
        # Calcul de la valeur de retour entre -1 et 1
        valeur = -math.cos(diff_rad)
        valeurs.append(valeur)
    
    # Retourne la liste de valeurs
    print(valeurs)
    print(len(valeurs))
    #plt.plot(distances,valeurs)
    # Tracer le graphe
    fig, ax = plt.subplots()
    ax.plot(distances, valeurs)

    # Ajouter une ligne noire pour le 0
    ax.axhline(y=0, color='black', linewidth=0.5)

    # Ajouter une zone verte de 0 à 1
    ax.axhspan(0, 1, facecolor='lightgreen', alpha=0.5)
    ax.text(5, 0.5, 'The wind is in your back, it helps you', fontsize=12, color='darkgreen')


    # Ajouter une zone rouge de 0 à -1
    ax.axhspan(-1, 0, facecolor='lightcoral', alpha=0.5)
    ax.text(5, -0.5, 'The wind is from the front, you will have to fight it', fontsize=12, color='maroon')


    # Définir les limites de l'axe des ordonnées
    plt.title("The strength of the wind -- Paris Marathon -- 02/04 09:00am")
    plt.xlabel("distance in km")
    plt.ylabel("wind help (normalised) ")
    ax.set_ylim(-1, 1)
    plt.show()
    return valeurs
    







def plot_elevation(file_path):
    gpx_file = open(file_path, 'r')
    gpx = gpxpy.parse(gpx_file)

    data = []
    last_distance = 0
    last_elevation = gpx.tracks[0].segments[0].points[0].elevation
    last_point = gpx.tracks[0].segments[0].points[2]


    for point in gpx.tracks[0].segments[0].points:
        distance = gpxpy.geo.haversine_distance(
            last_point.latitude, last_point.longitude,
            point.latitude, point.longitude
        )
        last_point = point

        if distance >= 480:  # distance en mètres
            data.append((last_distance / 480, last_elevation))
            last_distance = 0

        last_elevation = point.elevation
        last_distance += distance

    data.append((last_distance / 480, last_elevation))
    print(data)
    print(len(data))

    plt.plot(data[0],data[1])
    plt.xlabel("Distance (km)")
    plt.ylabel("Altitude (m)")
    plt.title("Profil d'altitude")
    plt.show()





import matplotlib.pyplot as plt

def calculate_pace(target_time, distance = 42.195):
    # Calcul de l'allure moyenne à respecter
    pace_sec = target_time*60 / distance
    
    # Calcul des minutes et secondes correspondant à l'allure
    pace_min = int(pace_sec // 60)
    pace_sec = int(pace_sec % 60)
    
    # Formatage de la chaîne de caractères de l'allure
    return f"{pace_min:02d}:{pace_sec:02d}"

def marathon_plan(target_time):
    # Calcul de l'allure moyenne à respecter
    pace = target_time / 42.195
    
    # Calcul des allures par kilomètre
    A = [0.9999199522,1.040255691,0.9746651939,0.9960502828,1.005183958,0.992342894,0.9991518074,0.9832673854,0.9847204184,1.041915395,1.027872258,0.9632507696,0.977212401,1.004337191,0.986988376,1.011342561,1.012075405,1.020133744,1.025945886,1.011082082,1.019554566,1.031524278,0.9749368565,1.002018091,1.006842095,1.003043413,0.9972968199,0.9965717622,0.978048401,0.9641389987,0.9570114856,0.958754244,0.9561776729,0.9574253594,1.006115508,0.9975282232,1.027123111,1.042187082,1.009894292,1.009894292,1.019400481,1.026799315,1.027348473]
    B = [pace * x for x in A]
    """
    # Tracé de la courbe d'allures par kilomètre
    distances = list(range(1, 44))
    plt.bar(distances, B)
    plt.title("Personalized Pace")
    plt.xlabel("Distance (km)")
    plt.ylabel("Pace (min/km)")
    plt.ylim(min(B)-0.05,max(B)+0.05)
    plt.show()
    

    
    # Affichage des temps de passage aux kilomètres
    print("Temps de passage aux kilomètres :")
    for i in range(len(km_times)):
        total_minutes = times[i] 
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        seconds = int((total_minutes % 1) * 60)
        print(f"{km_times[i]:>6} km : {hours:02d}h{minutes:02d}min{seconds:02d}s")

    """
    # Convertir les allures en minutes:secondes
    B_str = []
    for pace in B:
        min_pace = math.floor(pace)
        sec_pace = math.floor((pace - min_pace) * 60)
        B_str.append(f"{min_pace:02d}:{sec_pace:02d}")
        
    # Tracé de la courbe d'allures par kilomètre
    distances = list(range(1, 44))
    plt.bar(distances, B)
    plt.title("Personalized Pace. Pace for each km")
    plt.xlabel("pace (min:sec/km)")
    plt.ylabel("Pace (min/km)")
    plt.xticks(distances, B_str, rotation=45, ha="right",fontsize=6)
    plt.ylim(min(B)-0.05, max(B)+0.05)
    
    # Enregistrement de l'image
    plt.savefig('marathon_plan.png', dpi=300, bbox_inches='tight')
    
    # Fermeture de la figure pour éviter l'affichage
    plt.close()

    return B















#elevation_gain_per_km("Paris2023.gpx")
#elevation_gain_per_km2("Paris2023.gpx")
#plot_elevation("Paris2023.gpx")
#calculate_orientation("Paris2023.gpx")
#impact_vent_liste(19)
#marathon_plan(180)
#marathon_pace(180)





"""


from reportlab.pdfgen import canvas

# créer un nouveau document PDF
pdf = canvas.Canvas("existing_document.pdf")


# ajouter les images
pdf.drawImage("strava_logo.pdf", 30, 600, width=250, height=125)
pdf.drawImage("logo_enduraw.pdf", 300, 600, width=250, height=125)

# sauvegarder le document PDF
pdf.save()
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Créer un nouveau document PDF
pdf = canvas.Canvas("existing_document.pdf", pagesize=A4)

# Dessiner les logos de Strava et Enduraw en haut de la page
strava_logo = ImageReader("strava_logo.png")
pdf.drawImage(strava_logo, 30, 750, width=100, height=100, mask='auto')

enduraw_logo = ImageReader("logo_enduraw.png")
pdf.drawImage(enduraw_logo, 430, 750, width=100, height=100, mask='auto')

# Sauvegarder le document PDF
pdf.save()

















import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader
from PIL import Image


def create_pacing_plan(name, target_time):
    # Création du document PDF
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    pace = 0 

    # Ajout des éléments sur la première page
    can.setFont("Helvetica-Bold", 16)
    can.drawString(225, 750, "Enduraw Pacing Plan")
    can.setFont("Helvetica", 14)
    can.drawString(225, 725, "Paris marathon 02/04/23")
    #can.drawImage("strava_logo.png", 30, 720, 110, 50)
    #can.drawImage("logo_enduraw.png", 450, 720, 110, 50)
    can.drawString(80, 700, f"Personalized for {name}, according to the elevation and the wind")
    can.drawImage("image1.png", 10, 535, 300, 150)
    can.drawImage("image2.png", 300, 535, 300, 150)
    can.showPage()

    # Ajout des éléments sur la deuxième page
    can.setFont("Helvetica-Bold", 16)
    can.setFillColorRGB(1, 0, 0) # définir la couleur de remplissage à rouge

    # calculer la largeur du texte
    text_width = can.stringWidth(f"Your goal is : {target_time} minutes")
    # récupérer la largeur de la page
    page_width, _ = letter
    # calculer les coordonnées du centre
    x = page_width/2
    y = 520
    can.drawCentredString(x, y, f"Your goal is : {target_time} minutes")

    can.setFillColorRGB(0, 0, 0) # noir
    can.line(30, 510, 550, 510)
    
    pace = calculate_pace(target_time)
    can.drawString(200, 490, f"Wich means : {pace} min/km")

    can.drawString(230, 460, f"Good luck {name}")

    #can.line(30, 470, 550, 470)

    
    can.setFont("Helvetica-Bold", 14)
    can.drawString(5, 345, "Prediction time :")
    km_times = [5, 10, 15, 20, 21.1, 25, 30, 35, 40, 42.2]
    times = []
    for km in km_times:
        time = 0
        for i in range(int(km)):
            time +=  marathon_plan(target_time)[i]
        times.append(time)
    for i in range(len(km_times)):
        can.drawString(5, 300 - i*25, f"{km_times[i]:>6} km : {int(times[i])} min {(times[i] % 1) * 60:.0f} s")
    can.drawImage("marathon_plan.png", 170, 60, 400, 350)
    can.setFont("Helvetica", 10)
    can.drawString(30, 30, "This pacing strategy has been proposed by Enduraw. Subscribe on Instagram or LinkedIn for more data insights.")
    can.save()

    # Fusion des pages pour créer un document PDF complet
    packet.seek(0)
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(open("existing_document.pdf", "rb"))
    output = PdfWriter()
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    page.merge_page(new_pdf.pages[1])
    output.add_page(page)
    outputStream = open("new_document.pdf", "wb")
    output.write(outputStream)
    outputStream.close()



create_pacing_plan("anatole",167)






