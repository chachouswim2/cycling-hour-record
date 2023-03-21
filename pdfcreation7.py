import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Chargement du fichier json
with open("/Users/Joseph/Downloads/streams.json", "r") as json_file:
    data = json.load(json_file)

# Récupération des données nécessaires pour les graphes
altitude = data["altitude"]
distance = data["distance"]
heartrate = data["heartrate"]
velocity_smooth = data["velocity_smooth"]
grade_adjusted_speed = data["grade_adjusted_speed"]

# Calcul des valeurs moyennes
heartrate_mean = sum(heartrate) / len(heartrate)
velocity_mean = sum(velocity_smooth) / len(velocity_smooth)
grade_adjusted_speed_mean = sum(grade_adjusted_speed) / len(grade_adjusted_speed)

# Création du pdf
pdf_file = PdfPages("race_report8.pdf")

# Première page
plt.suptitle("{} - Race Report".format(data["name"]), color="#FFA500", fontsize=24)


fig, axs = plt.subplots(2, 1, figsize=[8.27, 11.69], dpi=100)
fig.set_facecolor("#0000FF")

# Graphe de l'altitude
axs[0].plot(distance, altitude, color="#FF0000")
axs[0].set_xlabel("Distance (km)", fontsize=14)
axs[0].set_ylabel("Altitude (m)", fontsize=14)

# Graphe de la fréquence cardiaque
axs[1].plot(distance, heartrate, color="#FFA500")
axs[1].set_xlabel("Distance (km)", fontsize=14)
axs[1].set_ylabel("Fréquence cardiaque (bpm)", fontsize=14)

pdf_file.savefig(fig)
plt.close()

# Deuxième page
fig = plt.figure(figsize=[8.27, 11.69], dpi=100)
fig.set_facecolor("#0000FF")

# Tableau des valeurs moyennes
plt.table(cellText=[["Fréquence cardiaque", "Vitesse", "VAP"], [heartrate_mean, velocity_mean, grade_adjusted_speed_mean]], colLabels=None, cellLoc="center", loc="center")

# Logo Strava
strava_logo = plt.imread("/Users/Joseph/Downloads/strava_logo.png")
plt.imshow(strava_logo, extent=[0, 0.2, 0, 0.2], aspect="auto", origin="lower", alpha=0.8, zorder=1)

# Texte en bas de la page
plt.text(0, -0.1, "Rapport présenté par Joseph Mestrallet", fontsize=12, color="#FF0000", ha="left")

pdf_file.savefig(fig)
plt.close()
