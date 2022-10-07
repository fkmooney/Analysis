from flask import Flask,  render_template

import requests
import pandas as pd

app = Flask(__name__)

@app.route('/',)
def hourly():

    try:
        url = 'https://api.weather.gov/points/40.6722,-73.9668'
        res = requests.get(url)
        text = (res.json())
        forecast_url = (text['properties']['forecast'])
        forecastHourly_url = (text['properties']['forecastHourly'])

        res = requests.get(forecastHourly_url)
        text = (res.json())
        dfh = pd.DataFrame.from_dict(text['properties']['periods'])
        dfh = dfh.drop(['number', 'name','temperatureUnit', 'icon', 'detailedForecast'], axis=1)
        forecastHourly = dfh.to_html()

    except:
        Weather_Summary = "not available"
        Temperature = "not available"

    return render_template("index.html",
        forecastHourly=forecastHourly,
        )

@app.route('/extended',)
def extended():

    try:
        url = 'https://api.weather.gov/points/40.6722,-73.9668'
        res = requests.get(url)
        text = (res.json())
        forecast_url = (text['properties']['forecast'])
        forecastHourly_url = (text['properties']['forecastHourly'])

        res = requests.get(forecast_url)
        text = (res.json())
        df = pd.DataFrame.from_dict(text['properties']['periods'])
        df = df.drop(['number', 'temperatureUnit', 'icon'], axis=1)
        forecast = df.to_html()

    except:
        Weather_Summary = "not available"
        Temperature = "not available"

    return render_template("extended.html",
        forecast=forecast, 
        )
    
