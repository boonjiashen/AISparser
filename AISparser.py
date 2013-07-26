"""Parses marinetraffic.com for AIS data"""
#import urllib2
from bs4 import BeautifulSoup
import requests
import re
import os  # for os.walk
import matplotlib.pyplot as plt
import numpy as np

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

def get_next_page(src):
    """Returns the URL of the next page given a page source"""

    soup = BeautifulSoup(src)
    images = soup.find_all('img', alt='Next page')
    if len(images) < 1:
        return None
    next_URL = images[0].parent.get('href')

    return next_URL

def get_ship_links(src):
    """Returns a list of (ship_name, ship_URL) tuples parsed from a page"""

    soup = BeautifulSoup(src)
    tags = soup.find_all(href=re.compile("shipdetails"))
    names = [tag.string for tag in tags]
    URLs = [tag.get('href') for tag in tags]

    return zip(names, URLs)

def get_page_no(src):
    """Returns the page number of a ship catalog page source"""

    soup = BeautifulSoup(src)
    tags = soup.find_all('font',color="#800000",face="Tahoma")
    assert len(tags) > 0
    match = re.search('page(.*)/', tags[0].string)
    page_no = match.group(1)

    return page_no

#def main():
if True:
    root_URL = 'http://www.marinetraffic.com/ais/'

##    # Parses the downloaded ship pages
##    folder = 'ships'
##    ship_local_paths = [os.path.join(folder, filename)
##        for (dirpath, dirnames, filenames) in os.walk(folder)
##        for filename in filenames]
##    ships_data = []
##    for ship_local_path in ship_local_paths:
##        with open(ship_local_path, 'r') as fid:
##            ship_src = fid.read().decode('utf8')
##        ship_data = get_ship_data(ship_src)
##        print ship_local_path, len(ship_data.items())
##        ships_data.append(ship_data)
##
##    ships_data = [x for x in ships_data if len(x.items()) == 5]
##    plt.close('all')
##    plt.figure()
##    for ship_data in ships_data:
##        length = ship_data['LOA (Length Overall):']
##        draft = ship_data['Draft (max):']
##        plt.plot(length, draft, 'r.')
##    plt.show()


##    # Downloads all the ship pages from downloaded catalog pages
##    folder = 'B'
##    catalog_files = [os.path.join(folder, filename)
##        for (dirpath, dirnames, filenames) in os.walk(folder)
##        for filename in filenames]
##    for catalog_file in catalog_files:
##        with open(catalog_file , 'r') as fid:
##            catalog_src = fid.read().decode('utf8')
##        for ship_name, ship_URL in get_ship_links(catalog_src):
##            ship_local_path = os.path.join('ships', ship_name)
##            if os.path.isfile(ship_local_path):
##                print ship_local_path, 'skipped because file already exists'
##                continue
##            ship_src = get_src(root_URL + ship_URL)
##            try:
##                with open(ship_local_path, 'w') as fid:
##                    fid.write(ship_src.encode('utf8'))
##                    print ship_URL, ship_name, 'created'
##            except IOError:
##                print ship_name, 'skipped due to IOError'


##    ship_links = [x for src in catalog_sources for link in get_ship_links]
##    print files

    foo = 'http://www.marinetraffic.com/ais/datasheet.aspx?datasource=SHIPS_CURRENT&alpha='
    alphabets = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    seed_URL = 'http://www.marinetraffic.com/ais/datasheet.aspx?datasource=SHIPS_CURRENT&alpha=C&mode='

    # Goes down the catalog of ships beginning with the same alphabet
    next_URL = seed_URL
    while True:
        src = get_src(seed_URL)
        page_no = get_page_no(src)
        with open('C/' + page_no, 'w') as fid:
            fid.write(src.encode('utf8'))
        next_URL = get_next_page(src)
        print next_URL
        if not next_URL:
            break

##    for name, leaf_URL in get_ship_links(src):
##
##        # Drop names that are too short
##        if len(name) == 1:
##            continue
##
##        ship_src = get_src(root_URL + leaf_URL)
##        ship_data = get_ship_data(ship_src)
##        print name, ship_data
##
##        with open('ships/' + name, 'w') as fid:
##            fid.write(src.encode('utf8'))
##        with open(name, 'r') as fid:
##            incoming_src = fid.read().decode('utf8')