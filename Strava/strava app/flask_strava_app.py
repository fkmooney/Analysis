import os
import glob
from flask import Flask, redirect, url_for, render_template
from flask import request, session
from flask import send_from_directory
from werkzeug.utils import secure_filename

import base64
from io import BytesIO
from matplotlib.figure import Figure

#######################################
import gpxpy
import gpxpy.gpx
import geopy.distance
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import seaborn as sns
from typing import Dict, Union
from datetime import datetime
from numpy_ext import rolling_apply
import numpy as np

import bs4
import requests
import ast

# Apply the default theme
sns.set_theme()

plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
#########################################

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'gpx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1000 * 1000
app.secret_key = b'cnausidpbretqqretnbcnuiouib'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
            file.save(full_path)
            session['full_path'] = full_path
            return redirect(url_for('analysis', full_path=full_path))
    return render_template("index.html")

@app.route('/analysis')
def analysis():
    # Load gpx
    try:      
        full_path = request.args['full_path']
        full_path = session['full_path']
        gpx_path = full_path
    except:
        list_of_files = glob.glob('uploads/*.gpx')
        latest_file = max(list_of_files, key=os.path.getctime)
        gpx_path = latest_file
    
    with open(gpx_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    track = gpx.tracks[0]
    segment = track.segments[0]

    ####################################
    # process file into df

    # The XML namespaces used by the GPX file for extensions, used when parsing the extensions
    NAMESPACES = {'garmin_tpe': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'}

    # The names of the columns we will use in our DataFrame
    COLUMN_NAMES = ['latitude', 'longitude', 'elevation', 'time', 'heart_rate', ]

    def get_gpx_point_data(point: gpxpy.gpx.GPXTrackPoint) -> Dict[str, Union[float, datetime, int]]:
            """Return a tuple containing some key data about `point`."""
            
            data = {
                'latitude': point.latitude,
                'longitude': point.longitude,
                'elevation': point.elevation,
                'time': point.time}
        
            # Parse extensions for heart rate and cadence data, if available
            try:
                elem = point.extensions[0]  # Assuming we know there is only one extension
                data['heart_rate'] = int(elem.find('garmin_tpe:hr', NAMESPACES).text)
            except:
                data['heart_rate'] = 0
                
            return data

    segment = gpx.tracks[0].segments[0]  # Assuming we know that there is only one track and one segment
    data = [get_gpx_point_data(point) for point in segment.points]
    df = pd.DataFrame(data, columns=COLUMN_NAMES)

    # Cumulative distance.
    coords = [(p.latitude, p.longitude) for p in df.itertuples()]
    df['distance'] = [0] + [geopy.distance.distance(from_, to).m for from_, to in zip(coords[:-1], coords[1:])]
    df['cumulative_distance'] = df.distance.cumsum()
    df['cumulative_miles'] = 0.000621371 * df['cumulative_distance']

    # the below uses the speed embedded in the data, calling it realspeed
    ser = pd.array([0], dtype=float)
    for x in range(0,len(df)-1):
        speed = segment.get_speed(x)
        ser = np.append(ser,[speed])

    df['speed_in_meters'] = pd.Series(ser)
    df['realspeed'] = df['speed_in_meters'] * 2.23694 # convert to mph
    df['rolling_realspeed'] = df['realspeed'].rolling(10).mean() # using rolling average to smooth out

    ##############################################
    # get summary info for html
    Activity_Name = track.name
    Min_Elevation = "%.2f" % round(gpx.get_elevation_extremes()[0]*3.28084, 2)
    Max_Elevation = "%.2f" % round(gpx.get_elevation_extremes()[1]*3.28084, 2)
    Moving_Time = "%.2f" % round(segment.get_moving_data()[0]/60, 2)
    Stopped_Time = "%.2f" % round(segment.get_moving_data()[1]/60, 2)
    Moving_Distance = "%.2f" % round(segment.get_moving_data()[2]*0.000621371, 2)
    Stopped_Distance = "%.2f" % round(segment.get_moving_data()[3]*0.00062137, 2)
    Max_Speed = "%.2f" % round(df['rolling_realspeed'].max(), 2)
    Avg_Speed = "%.2f" % round(df['rolling_realspeed'].mean(), 2)
    Max_HR = "%.2f" % round(df['heart_rate'].max(), 2)
    Avg_HR = "%.2f" % round(df['heart_rate'].mean(), 2)

    ###############################################
    # graph speed vs heart rate vs elevation
    figure(figsize=(10, 4), dpi=80)

    x = df.cumulative_miles
    y1 = df.rolling_realspeed
    y2 = df.heart_rate
    y3 = df.elevation

    fig, ax1 = plt.subplots()
    fig.set_size_inches(10,4)

    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(("axes", 1.5))

    ax1.plot(x, y1, 'g-')
    ax2.plot(x, y2, 'b-')
    ax3.plot(x, y3, 'r:')

    ax1.set_xlabel('Miles')
    ax1.set_ylabel('Speed', color='g')
    ax2.set_ylabel('Heart Rate', color='b')
    ax3.set_ylabel('Elevation', color='r')

    ax2.grid(False)
    ax3.grid(False)

    ax1.set_ylim(0,50)
    ax2.set_ylim(df['heart_rate'].min()-10,190)
    ax3.set_ylim(gpx.get_elevation_extremes()[0]/5,gpx.get_elevation_extremes()[1]*1.5)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    graph1 = base64.b64encode(buf.getbuffer()).decode("ascii")

    #####################################################
    # the histogram of the data
    fig, ax1 = plt.subplots()
    fig.set_size_inches(5,4)
    n, bins, patches = plt.hist(df['heart_rate'], 10, range=(90,190))

    plt.xlabel('HR')
    plt.ylabel('Time')
    plt.title('Amount of Time Spent at Various Heart Rates')

    buf2 = BytesIO()
    fig.savefig(buf2, format="png")
    # Embed the result in the html output.
    graph2 = base64.b64encode(buf2.getbuffer()).decode("ascii")

    ####################################################
    # Plot Pie Chart
    fig, ax1 = plt.subplots()
    fig.set_size_inches(4,4)
    hr_count, division = np.histogram(df['heart_rate'], bins = [0, 109,147,159,170,200])
    hr_count = pd.DataFrame(hr_count)
    x = hr_count[0]

    labels = ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5']
    fig, ax = plt.subplots(figsize=(4, 4))

    patches, texts, pcts = ax.pie(
        x, labels=labels, pctdistance=0.8, # controls distance from center of %
        autopct='%.1f%%',
        wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
        textprops={'size': 'medium'},
        startangle=90)
    # For each wedge, set the corresponding text label color to the wedge's
    # face color.
    for i, patch in enumerate(patches):
      texts[i].set_color(patch.get_facecolor())
    plt.setp(pcts, color='white')
    plt.setp(texts, fontweight=600)
    ax.set_title('HR Zone')

    buf3 = BytesIO()
    fig.savefig(buf3, format="png")
    # Embed the result in the html output.
    graph3 = base64.b64encode(buf3.getbuffer()).decode("ascii")
    #################################################
    # Plot HR zones
    figure(figsize=(10, 4), dpi=80)

    x = df.cumulative_miles
    y = df.heart_rate
    y3 = df.elevation

    fig, ax1 = plt.subplots()
    fig.set_size_inches(10, 4)

    ax3 = ax1.twinx()
    ax1.plot(x, y, 'g-')
    ax3.plot(x, y3, 'r:')

    ax1.set_ylabel('Heart Rate', color='b')
    ax3.set_ylabel('Elevation', color='r')
    ax1.set_ylim(df['heart_rate'].min()-10,190)
    ax3.set_ylim(gpx.get_elevation_extremes()[0]/5,gpx.get_elevation_extremes()[1]*1.5)

    ax3.grid(False)

    ax1.axhline(y=109) # plot zone lines
    ax1.axhline(y=147)
    ax1.axhline(y=159)
    ax1.axhline(y=170)

    buf4 = BytesIO()
    fig.savefig(buf4, format="png")
    # Embed the result in the html output.
    graph4 = base64.b64encode(buf4.getbuffer()).decode("ascii")
    #####################################################
    # get weather for html

    lat = str(df['latitude'][0])[0:7]
    lon = str(df['longitude'][0])[0:8]
    date = df['time'][0].strftime('%Y-%m-%d')

    headers = {'User-Agent': 'Opera/9.80 (Windows NT 6.1; Win64; x64; Edition Next) Presto/2.12.388 Version/12.15',}
    try:
        url = "https://darksky.net/details/%s,%s/%s/us12/en" % (lat,lon,date)
        res = requests.get(url, headers=headers)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        dtime = df['time'][0]
        dtimestamp = str(round(dtime.timestamp()))
        
        # pull temp from soup using above timestamp
        all_scripts = soup.find_all('script')
        jsn = all_scripts[1].text[16:]
        jsn = jsn.split(dtimestamp[0:5])[1]
        jsn = "{" + jsn.split('visibility')[0][6:-2] + "}"

        jsn = ast.literal_eval(jsn)
        Weather_Summary = jsn.get("summary")
        Temperature = jsn.get("temperature")
        Feels_Like = jsn.get("apparentTemperature")
        Humidity = jsn.get("humidity")
        Windspeed = jsn.get("windSpeed")
        Precip_Intensity = jsn.get("precipIntensity")

    except:
        Weather_Summary = "not available"
        Temperature = "not available"
        Feels_Like = "not available"
        Humidity = "not available"
        Windspeed = "not available"
        Precip_Intensity = "not available"

    #####################################################
    return  render_template("analysis.html", 
        graph1=graph1, 
        graph2=graph2,
        graph3=graph3,
        graph4=graph4,

        Activity_Name=Activity_Name, 
        Min_Elevation=Min_Elevation, 
        Max_Elevation=Max_Elevation, 
        Moving_Time=Moving_Time, 
        Stopped_Time=Stopped_Time,
        Moving_Distance=Moving_Distance, 
        Stopped_Distance=Stopped_Distance, 
        Max_Speed=Max_Speed, 
        Avg_Speed=Avg_Speed, 
        Max_HR=Max_HR,
        Avg_HR=Avg_HR,

        Weather_Summary=Weather_Summary,
        Temperature=Temperature,
        Feels_Like=Feels_Like,
        Humidity=Humidity,
        Windspeed=Windspeed,
        Precip_Intensity=Precip_Intensity
        )
    