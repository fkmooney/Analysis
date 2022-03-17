from craigslist import CraigslistHousing

CraigslistHousing.show_filters()

cl_h = CraigslistHousing(site='newyork', 
                         filters={'zip_code': 11238, 
                         'max_price': 5000, 
                         'private_room': True,
                         'min_bedrooms': 2,
                         'max_bedrooms': 3})

for result in cl_h.get_results(sort_by='newest', geotagged=True):
    print(result)
