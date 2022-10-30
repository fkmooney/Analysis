import os
import glob
from flask import Flask, redirect, url_for, render_template
from flask import request, session
from werkzeug.utils import secure_filename

import base64
from io import BytesIO

#######################################
import geopy.distance
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import seaborn as sns
import numpy as np

import xml.etree.ElementTree as ET
from io import StringIO
from csv import writer


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

app.config['TRAP_HTTP_EXCEPTIONS']=True
@app.errorhandler(Exception)
def http_error_handler(error):
    return render_template('error.html')

@app.route('/analysis')
def analysis():
    # Load gpx
    try:
        full_path = request.args['full_path']
        full_path = session['full_path']
        gpx_path = full_path
    except:
        print(glob.glob('*'))
        list_of_files = glob.glob('mysite/uploads/*.gpx')
        print(glob.glob('*'))
        latest_file = max(list_of_files, key=os.path.getctime)
        gpx_path = latest_file

    ####################################
    # process file into df

    tree = ET.parse(gpx_path) # create element tree object
    root = tree.getroot() # get root element
    date = root[1][0].text

    output = StringIO()
    csv_writer = writer(output)
    COLUMN_NAMES = ['time','latitude', 'longitude', 'elevation', 'heart_rate', ]

    for elem in root[1][2]:
        ele = elem[0].text
        time = elem[1].text
        hr = elem[2][0][0].text
        lat = elem.get('lat')
        lon = elem.get('lon')
        row = [time, lat, lon, ele, hr]
        csv_writer.writerow(row)

    output.seek(0) # we need to get back to the start of the BytesIO
    df = pd.read_csv(output, header=None, names=COLUMN_NAMES)


    # Cumulative distance.
    coords = [(p.latitude, p.longitude) for p in df.itertuples()]
    df['distance'] = [0] + [geopy.distance.distance(from_, to).m for from_, to in zip(coords[:-1], coords[1:])]
    df['cumulative_distance'] = df.distance.cumsum()
    df['cumulative_miles'] = 0.000621371 * df['cumulative_distance']
    df['time']= pd.to_datetime(df['time'])
    df['cumulative_time'] = df['time']-df['time'].min()
    df['cumulative_time'] =df['cumulative_time'] / np.timedelta64(1, 'm')

    df['time_diff'] = (df['time'] - df['time'].shift(+1)) / pd.Timedelta(seconds=1)
    df['speed_mph'] = df['distance']/df['time_diff']  * 2.23694 # convert to mph
    df['rolling_realspeed'] = df['speed_mph'].rolling(10).mean()

    ##############################################
    # get summary info for html
    Min_Elevation = "%.2f" % round(df['elevation'].min(), 2)
    Max_Elevation = "%.2f" % round(df['elevation'].max(), 2)
    Moving_Time = round(df['cumulative_time'].max() - (len(df[(df['distance'] < 0.5)]) / 60), 2)
    Stopped_Time = round(len(df[(df['distance'] < 0.5)]) / 60, 2)
    Total_Distance = "%.2f" % round(df['cumulative_miles'].max(), 2)
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

    return  render_template("analysis.html",
        graph1=graph1,
        graph2=graph2,
        graph3=graph3,
        graph4=graph4,

        Activity_Name=date,
        Min_Elevation=Min_Elevation,
        Max_Elevation=Max_Elevation,
        Moving_Time=Moving_Time,
        Stopped_Time=Stopped_Time,
        Total_Distance=Total_Distance,
        Max_Speed=Max_Speed,
        Avg_Speed=Avg_Speed,
        Max_HR=Max_HR,
        Avg_HR=Avg_HR,

        )
