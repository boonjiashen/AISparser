"""Parses marinetraffic.com for AIS data"""
#import urllib2
from bs4 import BeautifulSoup
import requests
import re

def ship_src2data(src):
    """Returns ship data parsed from the source code of a ship page
    """

    fields = """
LOA (Length Overall)
Beam
Draft (max)
    """.strip().splitlines()
    soup = BeautifulSoup(src)
    boat_data = {}
    for field in fields:
        tags = [tag for tag in soup.find_all('b') if tag.string.find(field) != -1]
#        tags = soup.find_all(text=field)
#        assert len(tags) == 1
        # There are fields that are empty, sometimes don't even exist
        # Empty field http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=538004700
        # No field    http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=413854231
        if len(tags) != 1:
            return None
        string = tags[0].nextSibling.string
        if string.isspace() or not string:
            return None
        value = float(string)
        boat_data[field] = value
    return boat_data

root_URL = 'http://www.marinetraffic.com/ais/'
#ship_URL = "http://www.marinetraffic.com/ais/shipdetails.aspx?imo=9524451"
#src = requests.get(URL).text
all_ships_URL = 'http://www.marinetraffic.com/ais/datasheet.aspx?datasource=SHIPS_CURRENT&alpha=A&level0=200'
URL = all_ships_URL
src = requests.get(URL).text
soup = BeautifulSoup(src)
#tags = soup.find_all('a')
tags = soup.find_all(href=re.compile("shipdetails"))
names = [tag.string for tag in tags]
URLs = [root_URL + tag.get('href') for tag in tags]

found = False
for name, URL in zip(names, URLs):
    is_PUSAN = name.find('PUSAN') != -1
    if is_PUSAN:
        found = True
    elif not found:
        continue
    src = requests.get(URL).text
    ship_data = ship_src2data(src)
    print name, ship_data
#URL = 'http://www.marinetraffic.com/ais/shipdetails.aspx?MMSI=897456478'
#src = requests.get(URL).text
#data = ship_src2data(src)

