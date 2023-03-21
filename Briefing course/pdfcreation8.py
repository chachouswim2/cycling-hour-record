import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from matplotlib.backends.backend_pdf import FigureCanvasPdf
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing, Line
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageBreak

#json = "/Users/Joseph/Downloads/streams.json"
#PDF = "race_report8!"



# Fonction pour générer le PDF
def generate_pdf(json_file, pdf_file):
    # Charger les données à partir du fichier JSON
    with open(json_file) as f:
        data = json.load(f)






    
    # Initialiser le document PDF
    doc = SimpleDocTemplate(pdf_file, pagesize=A4, rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
    styles=getSampleStyleSheet()
    elements = []

    # Ajout du texte dans le pied de page
    def add_footer(canvas, doc):

        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        canvas.drawString(1*cm, 0.4*cm, "Rapport présenté par Joseph Mestrallet. Tous droits réservés ® Contactez moi pour plus d'informations")
        #canvas.drawImage("/Users/Joseph/Downloads/strava_logo.png", 0.2*cm, 0.2*cm,width=1*cm,height=1*cm)
        #canvas.drawImage(Image("/Users/Joseph/Downloads/strava_logo.png"),0.2*cm, 0.2*cm,width=1*cm,height=1*cm)
        canvas.restoreState()


    #Logo Strava
    logo_strava = Image("/Users/Joseph/Downloads/strava_logo.png")
    logo_strava.drawHeight = 0.5*inch
    #logo_strava.alignment = TA_LEFT   #permet de mettre un texte à droite ou à gauche ou de le justifier 
    logo_strava.vAlign = "BOTTOM"
    logo_strava.drawWidth = 0.5*inch
    logo_strava.hAlign = "RIGHT"
    #logo_strava.x = 50*cm
    #logo_strava.y = 200*cm
    elements.append(logo_strava)



    # Titre
    style = ParagraphStyle(  name='test', fontName = "Courier", alignment=1, borderColor = "black" )  #doc dans le notion
    #getSampleStyleSheet()['Heading1']
    elements.append(Paragraph("<font size=24>{} Race Report</font>".format(data['name']), style))
    elements.append(Spacer(1, 20))

    # Titre 2
    style = ParagraphStyle(  name='test', fontName = "Courier", alignment=1, borderColor = "black" )  #doc dans le notion
    #getSampleStyleSheet()['Heading1']
    elements.append(Paragraph("<font size=24>{}</font>".format(data['race']), style))
    elements.append(Spacer(1, 20))

    # Sous titre
    style = ParagraphStyle(  name='test', fontName = "Courier", alignment=1, borderColor = "black" )  #doc dans le notion
    #getSampleStyleSheet()['Heading1']
    elements.append(Paragraph("<font size=8> Ce rapport est une analyse de vos données de course. Il utilise les données de votre compte Strava et des algorithmes développés dans le cadre de ma master thesis, en collaboration avec les athlètes professionnels avec lesquels je travaille </font>", style))




    # Récupérer les données 
    altitude = data["altitude"]
    distance = data["distance"]
    runner_name = data["name"]
    heartrate = data["heartrate"]



# test avec matplotlib

    # Création du graphique avec matplotlib
    #graphique de la distance 
    fig, ax = plt.subplots()
    plt.title("Profil altimétrique de la course" , color='#ffa600')
    #plt.figure(figsize=(8.27, 11.69))
    #fig.set_figwidth(12) # Largeur de 8 pouces
    #fig.set_figheight(2) # Hauteur de 6 pouces
    plt.xlabel('Distance (m)')
    plt.ylabel('Elevation (m)')
    ax.plot(distance, altitude)
    # Convertion du graphique en objet Image
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    im = Image(buf, width=400, height=200)
    # Ajout de l'image au pdf
    elements.append(im)





    # Création du graphique avec matplotlib
    #graphique de la HR et altitude
    fig, ax = plt.subplots()
    if 'distance' in data:
    
        
        ax.plot(distance, altitude, label='dénivelé')
        ax2 = ax.twinx()
        ax2.plot(distance, heartrate, color='r', label='Fréquence cardiaque')

    else :
        ax.text(0.5, 0.5, "No Data", fontsize=18, ha='center')
        ax.text(0.5, 0.3, "J'ai besoin d'avoir un accès plus complet à votre compte Strava", fontsize=8, ha='center')

    plt.title("Dénivelé et FC en fonction de la distance" , color='#ffa600')
    #plt.figure(figsize=(8.27, 11.69))
    #fig.set_figwidth(12) # Largeur de 8 pouces
    #fig.set_figheight(2) # Hauteur de 6 pouces
    # Ajout des légendes
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Altitude (m)')
    ax2.set_ylabel('Fréquence cardiaque (bpm)')
    ax.legend()
    ax2.legend()
    #plt.xlabel('Distance (m)')
    #plt.ylabel('Fréquence cardiaque (bpm)')
    
    # Convertion du graphique en objet Image
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    im = Image(buf, width=400, height=200)
    # Ajout de l'image au pdf
    elements.append(im)
    

    
        
  




    # Création du graphique avec matplotlib
    #graphique de la HR 
    fig, ax = plt.subplots()
    if 'distkance' in data:
    
        ax.plot(distance, heartrate)
    else :
        ax.text(0.5, 0.5, "No Data", fontsize=18, ha='center')
        ax.text(0.5, 0.3, "J'ai besoin d'avoir un accès plus complet à votre compte Strava", fontsize=8, ha='center')

    plt.title("Profil de la FC en fonction de la distance" , color='#ffa600')
    #plt.figure(figsize=(8.27, 11.69))
    #fig.set_figwidth(12) # Largeur de 8 pouces
    #fig.set_figheight(2) # Hauteur de 6 pouces
    plt.xlabel('Distance (m)')
    plt.ylabel('Fréquence cardiaque (bpm)')
    # Convertion du graphique en objet Image
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    im = Image(buf, width=400, height=200)
    # Ajout de l'image au pdf
    elements.append(im)




    












    # # Graphe de profil de la course avec LinePlot (problème : on ne peut pas ajouter de légendes ...)
    # d = Drawing(250, 150)
    # lp = LinePlot()
    # lp.x = 50
    # lp.y = 0
    # lp.height = 125
    # lp.width = 300
    # lp.data = [list(zip(distance, altitude))]
    # lp.joinedLines = 1
    # lp.lines[0].strokeColor = colors.red
    # #lp.lines[0].__annotations__="altitude"

    # # Légende
    # legend = Paragraph("altitude", style=ParagraphStyle( name="légende graphe", fontName= "Helvetica", fontSize= 10))
    # legend.x = 400
    # legend.y = 150
    # legend.colorNamePairs = [("altitude")]
    # d.add(lp)
    # #d.add(legend)

    # elements.append(d)
    # elements.append(legend)
    # elements.append(Spacer(10, 20))

    # # Graphe de fréquence cardiaque
    # heartrate = data["heartrate"]
    # d = Drawing(350, 250)
    # lp = LinePlot()
    # lp.x = 50
    # lp.y = -100
    # lp.height = 125
    # lp.width = 300
    # lp.data = [list(zip(distance, heartrate))]
    # lp.joinedLines = 1
    # lp.lines[0].strokeColor = colors.orange
    # d.add(lp)
    # elements.append(d)
    # elements.append(Spacer(1, 20))










    
    # # Graphe de profil d'altitude
    # altitude_data = [(data['distance'], data['altitude'])]
    # altitude_chart = LinePlot()
    # altitude_chart.x = 50
    # altitude_chart.y = 500
    # altitude_chart.height = 250
    # altitude_chart.width = 600
    # altitude_chart.data = [altitude_data]
    # altitude_chart.joinedLines = 1
    # altitude_chart.lines[0].strokeColor = colors.red
    # altitude_chart.lines.symbol = None
    # elements.append(altitude_chart)
    
    # # Graphe d'évolution de la fréquence cardiaque
    # heartrate_data = [(data['distance'], data['heartrate'])]
    # heartrate_chart = LinePlot()
    # heartrate_chart.x = 50
    # heartrate_chart.y = 50
    # heartrate_chart.height = 250
    # heartrate_chart.width = 600
    # heartrate_chart.data = [heartrate_data]
    # heartrate_chart.joinedLines = 1
    # heartrate_chart.lines[0].strokeColor = colors.orange
    # heartrate_chart.lines.symbol = None
    # elements.append(heartrate_chart)
    
    # Texte en bas
    #elements.append(Paragraph("<font color=red size=12>Rapport présenté par Juseph Mestrallet</font>",getSampleStyleSheet()['Normal']))
    
    #Deuxième page
    elements.append(PageBreak())
    # Tableau de moyennes
    moyenne_cardiaque = sum(data['heartrate'] ) / len(data['heartrate'])
    moyenne_vitesse = sum(data['velocity_smooth']) / len(data['velocity_smooth'])
    moyenne_VAP = sum(data['grade_adjusted_speed'] ) / len(data['grade_adjusted_speed'])
    data_table = [['Moyenne fréquence cardiaque', moyenne_cardiaque],
                  ['Moyenne vitesse', moyenne_vitesse],
                  ['Moyenne VAP', moyenne_VAP]]
    table = Table(data_table)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, -1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(table)

    elements.append(Spacer(10000, 200))

    #Texte en bas
    elements.append(Paragraph("<font color=red size=12>Rapport présenté par Jozeph Mestrallet</font>",
                              getSampleStyleSheet()['Normal']))

    elements.append(Spacer(10000, 200))


    elements.append(Paragraph("<font color=red size=12>Rapport présenté par Jozeph Mestrallet</font>",
                              getSampleStyleSheet()['Normal']))


    logo = Image("/Users/Joseph/Downloads/strava_logo.png")



    #doc.build(elements)
    #doc.multiBuild(elements)
    #template.build(elements)

    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)



# Générer le PDF
generate_pdf("/Users/Joseph/Downloads/streams.json", "race_report8-2.pdf")
