### NYC Housing Search ###

### Catpures max 120 per zip !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

### alternative is here: https://github.com/vikparuchuri/apartment-finder

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

#### define Extract Listing Data Function #######################################


def getZipListings(link):
    # Open the driver
    driver = webdriver.Firefox()
    driver.get(link)

    # Prepare the vectors
    titles = []
    dates = []
    prices = []
    bedrooms = []
    links = []

    # Extract the data
    items = driver.find_elements_by_class_name('result-info')
    for item in items:

        # Title
        try:
            titles.append(item.find_element_by_class_name('result-title').get_attribute('innerText'))
        except:
            titles.append("")

        # Date
        try:
            dates.append(item.find_element_by_class_name('result-date').get_attribute('datetime'))
        except:
            dates.append("")

        # Price
        try:
            prices.append(item.find_element_by_class_name('result-price').get_attribute('innerText'))
        except:
            prices.append("")

        # Bedrooms
        try:
            bedrooms.append(item.find_element_by_class_name('housing').get_attribute('innerText'))
        except:
            bedrooms.append("")

        # Link
        try:
            links.append(item.find_element_by_class_name('result-title').get_attribute('href'))
        except:
            links.append("")

    driver.close()
    data = [titles, dates, prices, bedrooms, links]
    df = pd.DataFrame(data).transpose() 
    df.columns = ['Title', 'Date', 'Price', 'Bedrooms', 'Link'] 

    return df

################################################

# Read in NYC Zip Codes
print('Load zips...')
zipcodes = pd.read_csv("nyc_zips.csv")

# Generate Craigslist Links
base_links = []
for i in range(0, len(zipcodes)):
    link = "https://newyork.craigslist.org/search/apa?postal={}&availabilityMode=0&sale_date=all+dates".format(zipcodes.iloc[i, 2])
    base_links.append(link)


# Loop over Zipcodes 
print('Loop over Zipcodes ...')
housing = pd.DataFrame()
for link in base_links:
    time.sleep(3)
    try:
        print("Trying: ", link)
        temp = getZipListings(link)
        temp['ZipCode'] = int(link[49:54])
        housing = housing.append(temp, sort=False)
        housing.to_csv("nyc-housing.csv", index=False)
    except:
        print("issue: ", link)
        time.sleep(5)  

housing = housing.merge(zipcodes, on='ZipCode', how='left')

# Rearrange columns for order
housing = housing[['Borough', 'Neighborhood', 'ZipCode', 'Date', 'Price', 'Bedrooms', 'Title', 'Link']]     


# Clean the Data
for i in range(0, len(housing)):
    try: 
        housing.iloc[i, 4] = housing.iloc[i, 4].replace('$', '')
    except: 
        housing.iloc[i, 4] = housing.iloc[i, 4]

    try: 
        housing.iloc[i, 5] = housing.iloc[i, 5].replace('\n', '')
    except: 
        housing.iloc[i, 5] = housing.iloc[i, 5]

    try: 
        housing.iloc[i, 5] = housing.iloc[i, 5].replace('-', '')
    except: 
        housing.iloc[i, 5] = housing.iloc[i, 5]

    try: 
        housing.iloc[i, 5] = housing.iloc[i, 5].strip()
    except: 
        housing.iloc[i, 5] = housing.iloc[i, 5]

    try:
        if housing.iloc[i, 5].find('br') == True:
            housing.iloc[i, 5] = housing.iloc[i, 5][0:3]
        else:
            housing.iloc[i, 5] = None
    except: 
        None

# Remove Duplictates
housing = housing.drop_duplicates(subset=['ZipCode', 'Price', 'Bedrooms', 'Title'], keep='first')

# Export the Data
housing.to_csv("nyc-housing.csv", index=False)


