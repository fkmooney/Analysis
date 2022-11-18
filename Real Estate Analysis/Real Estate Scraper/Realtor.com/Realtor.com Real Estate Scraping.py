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
pagelist = [*range(1, 9)]
for page in pagelist:
	url = "https://www.realtor.com/realestateandhomes-search/Wilton_CT/beds-2/type-single-family-home/price-250000-800000/lot-sqft-43560/show-recently-sold/pg-{0}?pos=41.661533,-74.160063,40.816831,-72.841703,10&qdm=true&points=%60mu_MeihyFmkHkgDqcL%7DfCghNmaF%7BpCgl%40quEk_%40gaKeoIujDumEqnBiaGpG_gEja%40sr%40rcAg_%40b%7B%40_%60CzpCimEhoF%7DfFtxJgmFzwFurA~lEe_%40xiK%3Fj%7DLsrApxUiRpnBnr%40faKlE%7CaOn_BlkHjfDfzGhlAj%7DA%60l%40ruExyD%60%7B%40plB%3F%60tFePf_%40qGtfDqnBtgGewBl%60DePptFor%40%60gDcPjoImgU~yBcsOlmCy%7BDdsAgsD%7C%60DewBoEywQq%60CwXmR%3F%7BXdPzX&view=map".format(page)
	
	html = requests.get(url=url,headers=header)
	print("Trying:" + url)

	# parse results
	soup = bs4.BeautifulSoup(html.text, 'html.parser')
	
	for card in soup.find_all('li',{'class':'jsx-1881802087 component_property-card'}):
		print(card)

		try:
			href = card.find('a',{'data-testid':'property-anchor'})
			href = (href['href'])
		except: 
			href = 'Error'

		try:
			location = card.find('img')
			location = (location['alt'])
		except: 
			location = 'Error'

		try:
			solddate = card.find('span',{'class':'jsx-3853574337 statusText'})
			solddate = solddate.text
		except: 
			solddate = 'Error'

		try:
			price = card.find('span',{'data-label':'pc-price-sold'})
			price = price.text
		except: 
			price = 'Error'

		try:
			beds = card.find('li',{'data-label':'pc-meta-beds'})
			beds = beds.text
		except: 
			beds = 'Error'

		try:
			baths = card.find('li',{'data-label':'pc-meta-baths'})
			baths = baths.text
		except: 
			baths = 'Error'

		try:
			sqft = card.find('li',{'data-label':'pc-meta-sqft'})
			sqft = sqft.text
		except: 
			sqft = 'Error'

		try:
			sqftlot = card.find('li',{'data-label':'pc-meta-sqftlot'})
			sqftlot = sqftlot.text
		except: 
			sqftlot = 'Error'



		df1 = pd.DataFrame({location:[solddate, price, beds, baths, sqft, sqftlot, href]})
		print(df1)
		df = pd.concat([df,df1], axis=1)
	time.sleep(1)


#output to csv
today = time.strftime("%Y%m%d")

df = df.transpose()
df = df.rename(columns={0:'solddate',1: 'price',2: 'beds',3: 'baths', 4: 'sqft',5: 'sqftlot',6: 'href' })
df.to_csv(today + "Realtorcom_Scraped_Listings.csv", index=True)
