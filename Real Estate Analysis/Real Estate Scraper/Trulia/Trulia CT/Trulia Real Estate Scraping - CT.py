print("starting script...")
import requests
import bs4
from bs4 import BeautifulSoup as soup
import pandas as pd
import time
import json
print("modules loaded...")


#create df
df = pd.DataFrame()

# Set Header
header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
	'referer': 'https://www.zillow.com/homes/for_rent/Manhattan,-New-York,-NY_rb/?searchQueryState=%7B%22pagination'}

# Send a get request: the below is just for agent listings, need a second pull
# for owner listings
pagelist = [*range(1, 21, 1)]
for page in pagelist:
	url = "https://www.trulia.com/sold/41.07516,41.47921,-73.86261,-73.21991_xy/2p_beds/450000-700000_price/SINGLE-FAMILY_HOME_type/11_zm/{0}_p/".format(page)

	html = requests.get(url=url,headers=header)
	print("Trying:" + url)

	# parse results
	soup = bs4.BeautifulSoup(html.text, 'html.parser')
	for card in soup.find_all('li',{'class':'Grid__CellBox-sc-144isrp-0 SearchResultsList__WideCell-b7y9ki-2 jiZmPM'}):

		try:
			coord = json.loads(card.find('script', type='application/ld+json').string)
			lat = coord['geo']['latitude']
			lon = coord['geo']['longitude']

		except: 
			lat = 'Error'
			lon = 'Error'

		
		try:
			coord = json.loads(card.find('script', type='application/ld+json').string)
			typ = coord['@type']
			locality = coord['address']['addressLocality']

		except: 
			locality = 'Error'
			typ = 'Error'

		try:
			location = card.find('div',{'data-testid':'property-address'})
			location = location['title']
		except: 
			location = 'Error'

		try:
			solddate = card.find('span',{'data-testid':'property-tag-1'})
			solddate = solddate.text
		except: 
			solddate = 'Error'

		try:
			price = card.find('div',{'data-testid': 'property-price'})
			price = price['title']
		except: 
			price = 'Error'

		try:
			beds = card.find('div',{'data-testid': 'property-beds'})
			beds = beds.get_text().strip()
		except:
			bed = 'Error'

		try:
			baths = card.find('div',{'data-testid': 'property-baths'})
			baths = baths.geoet_text().strip()
		except:
			baths = "Error"

		try:
			sqft = card.find('div',{'data-testid': 'property-floorSpace'})
			sqft = sqft.get_text().strip()
		except:
			sqft = "Error"

		try:
			zipc = location.rsplit(' ', 1)[1]

		except:
			zipc = "Error"
		
		df1 = pd.DataFrame({location:[price, typ, lat, lon, beds, baths, sqft, zipc, locality,solddate]})
		print(df1)
		df = pd.concat([df,df1], axis=1)
	time.sleep(1)


#output to csv
today = time.strftime("%Y%m%d")

df = df.transpose()
df = df.rename(columns={0:'price',1: 'typ',2: 'lat',3: 'lon', 4: 'beds',5: 'baths',6: 'sqft',7: 'zip code',8: 'locality',9: 'solddate', })
df.to_csv(today + "CT-Trulia_Scraped_Listings.csv", index=True)
