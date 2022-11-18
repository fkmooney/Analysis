import requests
import bs4
from bs4 import BeautifulSoup as soup
import pandas as pd


# Set Header
header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
  'referer': 'https://www.zillow.com/homes/for_rent/Manhattan,-New-York,-NY_rb/?searchQueryState=%7B%22pagination'}

# Send a get request:
url = "https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22usersSearchTerm%22%3A%22Hudson%2C%20NY%22%2C%22mapBounds%22%3A%7B%22west%22%3A-74.59742065722656%2C%22east%22%3A-72.99067016894531%2C%22south%22%3A41.70401896902793%2C%22north%22%3A42.52103616839696%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22price%22%3A%7B%22max%22%3A600000%7D%2C%22mp%22%3A%7B%22max%22%3A1457%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22customRegionId%22%3A%22dc7d461434X1-CRa89m0nsb4lfi_10k6h2%22%2C%22pagination%22%3A%7B%7D%7D"
html = requests.get(url=url,headers=header)

# parse results
soup = bs4.BeautifulSoup(html.text, 'html.parser')
#soup = soup.prettify()


for card in soup.find_all('article',{'class':'list-card list-card-additional-attribution list-card-additional-attribution-space list-card_not-saved'}):
	print(card)
	print("+++++++++++++++++++")


