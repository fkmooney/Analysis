from flask import Flask,  render_template

import requests
import pandas as pd
import bs4

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
        dfh['Time'] = pd.to_datetime(dfh['startTime'])
        dfh['Time'] = pd.to_datetime(dfh['Time'], format='%H:%M:%S').dt.strftime('%I:%M %p')
        dfh = dfh.rename(columns={"temperature": "Temp", "windSpeed": "Wind Speed", "shortForecast": "Forecast"})

        dfh2 = dfh[['Time', 'Temp', 'Wind Speed', 'Forecast']].copy()
        dfh2 = dfh2.iloc[0:12 , :]
        dfh2 = dfh2.set_index('Time')
        forecastHourly = dfh2.to_html()

        url = "https://forecast.weather.gov/MapClick.php?lat=40.7142&lon=-74.0059#.Y0IeG3bMI2w"
        res = requests.get(url)
        soup = bs4.BeautifulSoup(res.text, 'html.parser')
        current = soup.find("div", {"id": "current-conditions-body"})
        Temp = current.find("p", {"class": "myforecast-current-lrg"}).text
        Humidity = current.find("td", string="Humidity").findNext().findNext().text
        Barometer = current.find("td", string="Barometer").findNext().findNext().text
        Dewpoint = current.find("td", string="Dewpoint").findNext().findNext().text
        Visibility = current.find("td", string="Visibility").findNext().findNext().text

        curr_summary = dfh.loc[0, 'Forecast']


    except:
        Weather_Summary = "not available"
        Temperature = "not available"
        forecastHourly = "not available"
        Temp = "not available"
        Humidity = "not available"
        Barometer = "not available"
        Dewpoint = "not available"
        Visibility = "not available"
        curr_summary = "not available"


    return render_template("index.html",
        forecastHourly=forecastHourly,
        Temp=Temp,
        Humidity=Humidity,
        Barometer=Barometer,
        Dewpoint=Dewpoint,
        Visibility=Visibility,
        curr_summary=curr_summary
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
        df2 = df[['name', 'detailedForecast']].copy()
        df2 = df2.set_index('name')
        forecast = df2.to_html()
        forecast = forecast.replace("""<thead>
    <tr style="text-align: right;">
      <th></th>
      <th>detailedForecast</th>
    </tr>
    <tr>
      <th>name</th>
      <th></th>
    </tr>
  </thead>""", '')

    except:
        Weather_Summary = "not available"
        Temperature = "not available"
        forecast = "Not Available"

    return render_template("extended.html",
        forecast=forecast, 
        forecast=forecast,
        )
