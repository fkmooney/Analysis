#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import glob
import numpy as np


# In[2]:


# create df to hold aggregated data
df = pd.DataFrame()


# In[3]:


# grab scraped files 
for f in glob.glob('*.csv'):
    try:
        print("Trying: " + f)
        df2 = pd.read_csv(f)
        df2['Report'] = f
        df = pd.concat([df, df2])
        print("Done with " + f) 

    except:
        print("Error with " + f)


# In[4]:


df['Date'] = df['Report'].str[:8]
df['price1'] = df['price'].str[1:]
df.drop(df.loc[df['price1']=='rror'].index, inplace=True)
df['price1'] = df["price1"].str.replace(",", "").astype(float)
df.rename(columns={'Unnamed: 0': 'Address'}, inplace=True)
print(df.head())


# In[5]:


g = df.groupby(['price1']).count()
g


# In[6]:


# create export to play with in excel, has diff extension so wont interfere w future aggregations

import time
today = time.strftime("%Y%m%d")
df.to_csv(today + "TruliaAgggregated listings.txt", index=True, sep="|")


# In[7]:


table = pd.pivot_table(df, values='price1', index=['Date'], aggfunc='count')
table


# In[8]:


# below includes dupes
table = pd.pivot_table(df, values='price1', index=['Date'],columns='beds', aggfunc='count')
table


# In[9]:


table = pd.pivot_table(df, values='price', index=['Address'], columns='Date', aggfunc='count')
table


# In[10]:


# want to see how many new listings and how many delistings
# for some reason getting 1 more for each value than in excel

total_addresses = len(table.index)
print('Total Addresses: ', total_addresses)

delisted = table['20210922'].isna().sum()
print('Delisted: ' , delisted)

new = table['20210916'].isna().sum()
print('New: ' , new)


# In[11]:


# daily listing counts

table = pd.pivot_table(df, values='price1', index=['beds'], columns='Date', aggfunc='count', margins = True,
              fill_value = "")
table


# In[12]:


# zip code analysis
table = np.round(pd.pivot_table(df, values='price1', index=['zip code'], columns='beds', aggfunc=np.mean),1)
table


# In[13]:


import folium
map = folium.Map(location=[41.7004, -73.9210], default_zoom_start=15)


# In[14]:


#Create the dataframe containing the data we want to map.
tdf = table[['3bd']].copy()
tdf.rename(columns={'3bd': 'Price'}, inplace=True)
tdf['Zipcode'] = tdf.index.astype(str)
tdf.index.names = ['index']


# In[15]:


folium.Choropleth(geo_data="ny_new_york_zip_codes_geo.min.json",
               data=tdf, 
               columns=['Zipcode', 'Price'], 
               key_on='feature.properties.ZCTA5CE10', 
               fill_color='BuPu',fill_opacity=0.4,line_opacity=0.2,
               legend_name='SALE PRICE').add_to(map)
map


# In[16]:


# create map df
df2 = df[['zip code', 'lat', 'lon','price1','Address','beds']].copy()
df2 = df2[df2.beds != "4bd"]
df2 = df2[df2.beds != "2bd"]
df2 = df2[df2.beds != "5bd"]
df2 = df2[df2.beds != "6bd"]
df2 = df2[df2['lat'].notna()]
df2["lat"] = pd.to_numeric(df2["lat"]) 
df2["lon"] = pd.to_numeric(df2["lon"]) 
df2["zip code"] = pd.to_numeric(df2["zip code"])
df2


# In[17]:


test = df2.groupby('Address').mean()
test["zip code"] = test["zip code"].astype(int) 
test["price1"] = test["price1"].astype(int)
test


# In[18]:


from folium.plugins import MarkerCluster
marker_cluster = MarkerCluster().add_to(map) # create marker clusters


# In[19]:


# create count markers
for index, row in test.iterrows():
    folium.Marker([row['lat'], row['lon']],
                        tooltip = "Zipcode: {}".format([row['zip code']]),
                        popup="""<i>Mean sales price: </i> <br> <b>${}</b> """.format(round(row['price1'],2)),
                        ).add_to(marker_cluster)

map


# In[75]:


# look at price change over time for all 3 and 4 bd room houses
numbers = ["4bd", "3bd", "2bd", "5bd"]
dff = df[df["beds"].isin(numbers)]


# In[76]:


table = np.round(pd.pivot_table(dff, values='price1', index=['Date'], columns='beds', aggfunc=np.mean),1)
table.index = pd.to_datetime(table.index)
table


# In[77]:


import matplotlib.pyplot as plt


# In[79]:


# plot of price change over time

fig = plt.figure()
fig.set_figheight(7)
fig.set_figwidth(15)
ax = fig.add_subplot()

ax.plot(table)
ax.legend(['2bd','3bd', '4bd' ,'5bd'])


# In[ ]:



