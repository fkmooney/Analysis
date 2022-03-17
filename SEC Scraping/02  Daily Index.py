# import our libraries
import requests
import urllib
from bs4 import BeautifulSoup

# let's first make a function that will make the process of building a url easy.
def make_url(base_url , comp):
    
    url = base_url
    
    # add each component to the base url
    for r in comp:
        url = '{}/{}'.format(url, r)
        
    return url

# EXAMPLE
base_url = r"https://www.sec.gov/Archives/edgar/data"
components = ['886982','000156459019011378', '0001564590-19-011378-index-headers.html']
make_url(base_url, components)


# define a base url, this would be the EDGAR data Archives
base_url = r"https://www.sec.gov/Archives/edgar/data"

# define a company to search (GOLDMAN SACHS), this requires a CIK number that is defined by the SEC.
cik_num = '886982'

# let's get all the filings for Goldman Sachs in a json format.
# Alternative is .html & .xml
filings_url = make_url(base_url, [cik_num, 'index.json'])

# Get the filings and then decode it into a dictionary object.
content = requests.get(filings_url)
decoded_content = content.json()

# Get a single filing number, this way we can request all the documents that were submitted.
filing_number = decoded_content['directory']['item'][0]['name']

# define the filing url, again I want all the data back as JSON.
filing_url = make_url(base_url, [cik_num, filing_number, 'index.json'])

# Get the documents submitted for that filing.
content = requests.get(filing_url)
document_content = content.json()

# get a document name
for document in document_content['directory']['item']:
    if document['type'] != 'image2.gif':
        document_name = document['name']
        filing_url = make_url(base_url, [cik_num, filing_number, document_name])
        print(filing_url)

# define a base url, this would be the EDGAR data Archives
base_url = r"https://www.sec.gov/Archives/edgar/data"

# define a company to search (GOLDMAN SACHS), this requires a CIK number that is defined by the SEC.
cik_num = '886982'

# let's get all the filings for Goldman Sachs in a json format.
# Alternative is .html & .xml
filings_url = make_url(base_url, [cik_num, 'index.json'])

# Get the filings and then decode it into a dictionary object.
content = requests.get(filings_url)
decoded_content = content.json()

# Get a filing number, this way we can request all the documents that were submitted.
# HERE I AM JUST GRABBING CERTAIN FILINGS FOR READABILITY REMOVE [3:5] TO GRAB THEM ALL.
for filing_number in decoded_content['directory']['item'][3:5]:    
    
    filing_num = filing_number['name']
    print('-'*100)
    print('Grabbing filing : {}'.format(filing_num))
    
    # define the filing url, again I want all the data back as JSON.
    filing_url = make_url(base_url, [cik_num, filing_num, 'index.json'])

    # Get the documents submitted for that filing.
    content = requests.get(filing_url)
    document_content = content.json()

    # get a document name
    for document in document_content['directory']['item']:
        document_name = document['name']
        filing_url = make_url(base_url, [cik_num, filing_num, document_name])
        print(filing_url)


# define the urls needed to make the request, let's start with all the daily filings
base_url = r"https://www.sec.gov/Archives/edgar/daily-index"

# The daily-index filings, require a year and content type (html, json, or xml).
year_url = make_url(base_url, ['2019', 'index.json'])

# Display the new Year URL
print('-'*100)
print('Building the URL for Year: {}'.format('2019'))
print("URL Link: " + year_url)

# request the content for 2019, remember that a JSON strucutre will be sent back so we need to decode it.
content = requests.get(year_url)
decoded_content = content.json()

# the structure is almost identical to other json requests we've made. Go to the item list.
# AGAIN ONLY GRABBING A SUBSET OF THE FULL DATASET 
for item in decoded_content['directory']['item'][0:1]:
    
    # get the name of the folder
    print('-'*100)
    print('Pulling url for Quarter: {}'.format(item['name']))
    
    # The daily-index filings, require a year, a quarter and a content type (html, json, or xml).
    qtr_url = make_url(base_url, ['2019', item['name'], 'index.json'])
    
    # print out the url.
    print("URL Link: " + qtr_url)
    
    # Request, the new url and again it will be a JSON structure.
    file_content = requests.get(qtr_url)
    decoded_content = file_content.json()
    
    print('-'*100)
    print('Pulling files')

    # for each file in the directory items list, print the file type and file href.
    # AGAIN DOING A SUBSET
    for file in decoded_content['directory']['item'][0:10]:
        
        file_url = make_url(base_url, ['2019', item['name'], file['name']])
        print("File URL Link: " + file_url)


# define a url, in this case I'll just take one of the urls up above.
file_url = r"https://www.sec.gov/Archives/edgar/daily-index/2019/QTR2/master.20190401.idx"

# request that new content, this will not be a JSON STRUCTURE!
content = requests.get(file_url).content

# we can always write the content to a file, so we don't need to request it again.
with open('master_20190102.txt', 'wb') as f:
     f.write(content)


# let's open it and we will now have a byte stream to play with.
with open('master_20190102.txt','rb') as f:
     byte_data = f.read()

# Now that we loaded the data, we have a byte stream that needs to be decoded and then split by double spaces.
data = byte_data.decode("utf-8").split('  ')

# We need to remove the headers, so look for the end of the header and grab it's index
for index, item in enumerate(data):
    if "ftp://ftp.sec.gov/edgar/" in item:
        start_ind = index

# define a new dataset with out the header info.
data_format = data[start_ind + 1:]

master_data = []

# now we need to break the data into sections, this way we can move to the final step of getting each row value.
for index, item in enumerate(data_format):
    
    # if it's the first index, it won't be even so treat it differently
    if index == 0:
        clean_item_data = item.replace('\n','|').split('|')
        clean_item_data = clean_item_data[8:]
    else:
        clean_item_data = item.replace('\n','|').split('|')
        
    for index, row in enumerate(clean_item_data):
        
        # when you find the text file.
        if '.txt' in row:

            # grab the values that belong to that row. It's 4 values before and one after.
            mini_list = clean_item_data[(index - 4): index + 1]
            
            if len(mini_list) != 0:
                mini_list[4] = "https://www.sec.gov/Archives/" + mini_list[4]
                master_data.append(mini_list)
                
# grab the first three items
master_data[:3]


# loop through each document in the master list.
for index, document in enumerate(master_data):
    
    # create a dictionary for each document in the master list
    document_dict = {}
    document_dict['cik_number'] = document[0]
    document_dict['company_name'] = document[1]
    document_dict['form_id'] = document[2]
    document_dict['date'] = document[3]
    document_dict['file_url'] = document[4]
    
    master_data[index] = document_dict

# by being in a dictionary format, it'll be easier to get the items we need.
for document_dict in master_data[0:100]:

    # if it's a 10-K document pull the url and the name.
    if document_dict['form_id'] == '10-K':
        
        # get the components
        comp_name = document_dict['company_name']
        docu_url = document_dict['file_url']
        
        print('-'*100)
        print(comp_name)
        print(docu_url)

# Create a url that takes us to the Detail filing landing page
file_url_adj = docu_url.split('.txt')
file_url_archive = file_url_adj[0] + '-index.htm'

print('-'*100)
print('The Filing Detail can be found here: {}'.format(file_url_archive))

# Create a url that will take us to the archive folder
archive_url = docu_url.replace('.txt','').replace('-','')

print('-'*100)
print('The Archive Folder can be found here: {}'.format(archive_url))

# Create a url that will take us the Company filing Archive
company_url =docu_url.rpartition('/')

print('-'*100)
print('The Company Archive Folder can be found here: {}'.format(company_url[0]))

