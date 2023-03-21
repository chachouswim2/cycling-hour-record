import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Chargement des données à partir du fichier Json
with open('/Users/Joseph/Downloads/streams.json') as json_file:
    data = json.load(json_file)

# Récupération des données nécessaires pour les graphiques
altitude = data['altitude']
distance = data['distance']
heartrate = data['heartrate']
speed = data['grade_adjusted_speed']
speed2 = data['velocity_smooth']

# Calcul des valeurs moyennes
average_heartrate = sum(heartrate) / len(heartrate)
average_speed = sum(speed) / len(speed)
average_speed2 = sum(speed2) / len(speed2)

# Création du pdf
pdf_pages = PdfPages('race_report6.pdf')

# Première page
fig, axs = plt.subplots(2, 1, figsize=(11.69, 8.27))
axs[0].set_title(data['name'] + ' race report', color='orange')
axs[0].plot(distance, altitude, color='red')
axs[0].set_ylabel('Altitude (m)')
axs[0].set_xlabel('Distance (km)')
axs[1].plot(distance, heartrate, color='orange')
axs[1].set_ylabel('Heartrate (bpm)')
axs[1].set_xlabel('Distance (m)')
plt.figtext(0.5, 0.05, 'Rapport présenté par Joseph Mestrallet', color='red', ha='center')
pdf_pages.savefig()

# Deuxième page
plt.clf()
#fig, ax = plt.subplots(figsize=(11.69, 8.27))
plt.figtext(0.5, 0.5, f'Average heartrate: {average_heartrate} bpm\nAverage speed: {average_speed} km/h', ha='center')
pdf_pages.savefig()

# Fermeture du pdf
pdf_pages.close()

