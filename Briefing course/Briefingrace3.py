import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import xml.etree.ElementTree as ET
from matplotlib.backends.backend_pdf import PdfPages

def generate_pdf_with_maps(gpx_file, pdf_file):
    # Load GPX file
    tree = ET.parse(gpx_file)
    root = tree.getroot()
    
    # Extract track points
    ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    track_points = root.findall('.//gpx:trkpt', ns)
    lats = [float(x.attrib['lat']) for x in track_points]
    lons = [float(x.attrib['lon']) for x in track_points]

    # Set up basemap
    lat_center = sum(lats) / len(lats)
    lon_center = sum(lons) / len(lons)
    map = Basemap(projection='merc', lat_0=lat_center, lon_0=lon_center,
                  resolution='h', area_thresh=0.1,
                  llcrnrlon=min(lons), llcrnrlat=min(lats),
                  urcrnrlon=max(lons), urcrnrlat=max(lats))

    # Draw map
    fig, ax = plt.subplots(figsize=(8, 6))
    map.drawcoastlines()
    map.drawcountries()
    map.drawstates()
    map.fillcontinents(color='beige', lake_color='lightblue')
    map.drawmapboundary(fill_color='lightblue')

    # Draw track
    x, y = map(lons, lats)
    map.plot(x, y, 'bo-', markersize=2, linewidth=1)

    # Add title and footer
    title = "Briefing de " + gpx_file.split("/")[-1]
    plt.title(title)
    plt.text(0, -5, "Briefing développé par Joseph Mestrallet", fontsize=8)

    # Create PDF with empty plots
    with PdfPages(pdf_file) as pdf:
        pdf.savefig(fig)
        for i in range(7):
            pdf.savefig(plt.figure())

    plt.close()



generate_pdf_with_maps("eco.gpx", "brief2.pdf")