"""Parses marinetraffic.com for AIS data"""
#import urllib2
from bs4 import BeautifulSoup
import requests
import re

def get_src(URL):
    """Returns the page source from a URL"""
    #response = urllib2.urlopen(URL)
    #src = response.read()
    src = requests.get(URL).text

    return src

def is_number(s):
    """Checks if a string is a number"""
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_ship_data(src):
    """Returns ship data parsed from the source code of a ship page
    """

    fields = """
Length x Breadth:
Draught:
LOA (Length Overall):
Beam:
Draft (max):
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
            continue
        string = tags[0].nextSibling.string
        if string.isspace() or not string:
            continue
        elif is_number(string):
            value = float(string)
            if abs(value) < 0.1:
                continue
        else:
            value = string
        boat_data[field] = value

    return boat_data

##     <a href="datasheet.aspx?datasource=SHIPS_CURRENT&amp;alpha=A&amp;level0=200&amp;orderby=SHIPNAME&amp;sort_order=ASC&amp;var_page=2">
##      <img alt="Next page" border="0" height="11" src="icons/next.gif" width="9"/>
##     </a>

#def main():
if True:
    root_URL = 'http://www.marinetraffic.com/ais/'
    all_ships_URL = 'http://www.marinetraffic.com/ais/datasheet.aspx?datasource=SHIPS_CURRENT&alpha=A&level0=200'
    URL = all_ships_URL
    src = get_src(URL)

    soup = BeautifulSoup(src)
    tags = soup.find_all(href=re.compile("shipdetails"))

    # Find the URL of the next page

##    names = [tag.string for tag in tags]
##    URLs = [root_URL + tag.get('href') for tag in tags]
##
##    found = False
##    for name, URL in zip(names, URLs):
####        is_PUSAN = name.find('PUSAN') != -1
####        if is_PUSAN:
####            found = True
####        elif not found:
####            continue
##        if len(name) == 1:
##            continue
##        src = get_src(URL)
##        ship_data = get_ship_data(src)
##        print name, ship_data
##
##        with open(name, 'w') as fid:
##            fid.write(src.encode('utf8'))
##        with open(name, 'r') as fid:
##            incoming_src = fid.read().decode('utf8')
##        break