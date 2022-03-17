### NEXT STEPS: COMPARE TRAFFIC ON GOOGLE SEARCH AND BOOKSCAN SALES!!!!!!!!!!!!!!

import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# Enter paramaters
topic = "Avengers"
today = datetime.date.today()  # date of today
lastMonth = today - datetime.timedelta(days=800)  # date of 30 days prior
today = today.strftime(("%Y%m%d"))  # format for URL
lastMonth = lastMonth.strftime(("%Y%m%d"))  # format for URL

# Scrape and place in df
url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/%s/daily/%s/%s"%(topic, lastMonth, today) 

response = requests.get(url)  # reteive data from API url
your_json = response.json()  # format as json
df = pd.DataFrame(your_json['items'])  # read into df as a list
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H', )  # convert to datetime for resampling
df.set_index(df["timestamp"],inplace=True)  # set index for resampling 
df = df['views'].resample('W').sum()  # resample so views are grouped by week

print(df.head(20))
df.to_csv('Avengers_Wiki_Traffic.csv')

# plot by df
sns.set_style("whitegrid")
fig, ax = plt.subplots(1, 1)
ax.plot(df)
ax.xaxis.set_major_locator(ticker.MultipleLocator(15))  # set freq of x axis ticks
plt.title(topic + " Wikipedia Traffic")
plt.show()
