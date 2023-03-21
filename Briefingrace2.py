import gpxpy
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape, portrait
from reportlab.pdfgen import canvas
import pandas as pd
from datetime import datetime


def generate_briefing(gpx_file,filename):
    # Parse le fichier GPX et récupère les points de tracé
    gpx = gpxpy.parse(open(gpx_file, 'r'))
    track = gpx.tracks[0]
    segment = track.segments[0]
    points = segment.points

    # Calcule la distance entre chaque point
    distance = [0]
    for i in range(1, len(points)):
        prev_point = points[i-1]
        point = points[i]
        dist = prev_point.distance_2d(point)
        distance.append(distance[-1] + dist)

    # Calcule le dénivelé entre chaque point
    elevation = [p.elevation for p in points]
    ascent = [0]
    for i in range(1, len(elevation)):
        prev_elev = elevation[i-1]
        elev = elevation[i]
        diff = elev - prev_elev
        if diff > 0:
            ascent.append(ascent[-1] + diff)
        else:
            ascent.append(ascent[-1])



    # Génère le PDF avec les graphiques
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=portrait(letter))

    # Ajoute le titre dans le haut de la page
    pdf.setFont('Helvetica-Bold', 24)
    pdf.drawString(30, 750, 'Briefing 2 Course')

    # Ajoute la date et l'heure en haut à droite de la page
    date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    pdf.setFont('Helvetica', 10)
    pdf.drawString(500, 780, f'Date et heure : {date}')



    # Plot la courbe de dénivelé en fonction de la distance   graphique 1 
    plt.figure(figsize=(8, 6))
    plt.subplot(2, 2, 1)
    plt.plot(distance, elevation)
    plt.xlabel('Distance (km)')
    plt.ylabel('Dénivelé (m)')
    plt.title('Courbe de dénivelé')
    plt.grid()

    # Graphique 1 : Courbe de dénivelé en fonction de la distance
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(20, 450, 'Courbe de dénivelé en fonction de la distance')
    pdf.drawImage('elevation.png', 50, 500, width=300, height=200, preserveAspectRatio=True)




    #plt.close()
    #ax.remove()
    # Calcule le nombre de kilomètres par pourcentage de dénivelé    graphique 2 
    
    elev_diff = np.diff(elevation)
    #elev_diff = np.insert(elev_diff, 0, 0)
    grad = elev_diff / np.diff(distance)
    grad = np.insert(grad, 0, 0)
    _, bins, _ = plt.hist(grad, bins=20)
    plt.close()
    plt.subplot(2, 2, 2)
    plt.bar(range(len(bins)-1), height=[np.sum((grad >= bins[i]) & (grad < bins[i+1])) for i in range(len(bins)-1)])
    plt.xticks(range(len(bins)-1), ['{:.2f}% - {:.2f}%'.format(bins[i]*100, bins[i+1]*100) for i in range(len(bins)-1)], rotation=90)
    plt.xlabel('Pourcentage de dénivelé')
    plt.ylabel('Nombre de kilomètres')
    plt.title('Répartition des kilomètres par pourcentage de dénivelé')
    plt.grid()

    # Graphique 2 : Nombre de kilomètres par pourcentage de dénivelé
    #plt.close()
    plt.close()
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(350, 450, 'Nombre de kilomètres par pourcentage de dénivelé')
    plt.figure(figsize=(8, 6))
    
    _, bins, _ = plt.hist(grad, bins=20)
    #plt.close()
    percents = [(bins[i], bins[i+1]) for i in range(len(bins)-1)]
    counts = [np.sum((grad >= p[0]) & (grad < p[1])) for p in percents]
    km_by_percent = [(c / len(distance)) * 100 for c in counts]
    plt.bar([f'{p[0]:.1f}-{p[1]:.1f}%' for p in percents], km_by_percent, width=0.4)
    plt.xticks(rotation=45, ha='right')
    #plt.tight_layout()
    plt.savefig('km_by_percent.png')
    pdf.drawImage('km_by_percent.png', 300, 500, width=300, height=200, preserveAspectRatio=True)





    #3

    plt.close()
    # Plot le graphique vide
    plt.subplot(2, 2, 3)
    #plt.axis('off')
        
    # Graphique 3 : Graphique vide
    plt.close()
    # Créer un tableau vide
    x = np.array([])
    y = np.array([])

    # Tracer un graphique vide
    plt.plot(x, y)
    #plt.axis('off')

    # Enregistrer le graphique
    plt.savefig('empty_plot.png')
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(50, 250, 'Graphique vide')
    pdf.drawImage('empty_plot.png', 50, 300, width=300, height=200, preserveAspectRatio=True)










    plt.close()

    #4

    # Plot la courbe de dénivelé en fonction de la distance si le dénivelé est au-dessus de 10%
    high_elevation = [(d, e) for d, e in zip(distance, elevation) if e >= 10]
    if high_elevation:
        high_distance, high_elevation = zip(*high_elevation)
        plt.subplot(2, 2, 4)
        plt.plot(high_distance, high_elevation)
        plt.xlabel('Distance (km)')
        plt.ylabel('Dénivelé (m)')
        plt.title('Courbe de dénivelé (dénivelé > 10%)')
        plt.grid()
    
    
    
    # Graphique 4 : Courbe de dénivelé si le dénivelé est au-dessus de 10%

    plt.close()
    if high_elevation:
        pdf.setFont('Helvetica-Bold', 12)
        pdf.drawString(350, 250, 'Courbe de dénivelé si le dénivelé est au-dessus de 10%')
        #plt.figure(figsize=(5, 4))
        #plt.figure(figsize=(8, 6))
        plt.figure(figsize=(8, 6))
        plt.plot(high_distance, high_elevation)
        plt.xlabel('Distance (km)')
        plt.ylabel('Dénivelé (m)')
        plt.title('Courbe de dénivelé (dénivelé > 10%)')
        plt.grid()
        plt.tight_layout()
        plt.savefig('high_elevation.png')
        pdf.drawImage('high_elevation.png', 300, 300, width=300, height=200, preserveAspectRatio=True)


    plt.close()



    




    














    
    # Ajoute le footer
    pdf.setFont('Helvetica', 10)
    pdf.drawRightString(580, 20, 'Briefing développé par Joseph Mestrallet')

    # Sauvegarde le PDF et ferme le buffer
    pdf.save()
    buffer.seek(0)



    with open(filename, 'wb') as f:
        pdf_bytes = buffer.getvalue()
        f.write(pdf_bytes)
    return buffer
    print("le graphique a bien été généré")



generate_briefing("eco.gpx",'brief3course.pdf')