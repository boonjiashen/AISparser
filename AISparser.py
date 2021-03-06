"""Parses marinetraffic.com for AIS data"""
#import urllib2
from bs4 import BeautifulSoup
import requests
import re
import os  # for os.walk
import matplotlib.pyplot as plt
import numpy as np
from sys import stdout

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

def get_first_word_as_float(string):
    """Returns the first word in a string, cast as float"""

    list_of_words = string.split()

    return float(list_of_words[0])

def parse_length_x_breadth(string):
    """Parse the "Length x Breadth:" field"""

    length = get_first_word_as_float(string)
    breadth = get_first_word_as_float(string[string.find('X') + 1:])

    return (length, breadth)

# Defines the parsers for each field in ship specs page
parser_dict = {
"Length x Breadth:": parse_length_x_breadth,
"Draught:": get_first_word_as_float,
"LOA (Length Overall):": get_first_word_as_float,
"Beam:": get_first_word_as_float,
"Draft (max):": get_first_word_as_float,
}
fields = parser_dict.keys()

def get_ship_data(src):
    """Returns ship data parsed from the source code of a ship page"""

    soup = BeautifulSoup(src, "lxml")
    boat_data = {}
#    tags = soup.find_all(text=re.compile('|'.join(fields)))
    tags = soup.find_all(text=fields)
    for tag in tags:
        string = unicode(tag.parent.nextSibling.string)
        field = unicode(tag.string)
        if string.isspace() or not string or string.strip()[0] == '0':
            continue
        boat_data[field] = parser_dict[field](string)

    return boat_data

##     <a href="datasheet.aspx?datasource=SHIPS_CURRENT&amp;alpha=A&amp;level0=200&amp;orderby=SHIPNAME&amp;sort_order=ASC&amp;var_page=2">
##      <img alt="Next page" border="0" height="11" src="icons/next.gif" width="9"/>
##     </a>

def get_next_page(src):
    """Returns the URL of the next page or None if next page not found"""

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
    regex = r'page (\d+)/'
    tags = soup.find_all(text=re.compile(regex))
    assert len(tags) > 0
    match = re.search(regex, tags[0].string)
    page_no = match.group(1)

    return page_no

def download_ships_from_catalog(src, download_folder='ships', verbose=False):
    """Downloads all ship pages from a catalog page"""

    for ship_name, ship_URL in get_ship_links(src):
        ship_local_path = os.path.join(download_folder, ship_name)
        stdout.write(ship_local_path.ljust(30, ' '))
        if os.path.isfile(ship_local_path):
            if verbose:
                stdout.write(' skipped because file already exists\n')
            continue
        ship_src = get_src(root_URL + ship_URL)
        try:
            with open(ship_local_path, 'w') as fid:
                fid.write(ship_src.encode('utf8'))
                if verbose: stdout.write(' created\n')
        except IOError:
            if verbose: stdout.write(' skipped due to IOError\n')

def pickle_data_to_file(data, filename):
    import cPickle as pickle
    with open(filename, 'wb') as pkl:
        pickle.dump(data, pkl, -1)

def unpickle_from_file(filename):
    import cPickle as pickle
    with open(filename, 'rb') as pkl:
        data = pickle.load(pkl)

    return data

#def main():
if True:
    root_URL = 'http://www.marinetraffic.com/ais/'

#    # Parses the downloaded ship pages
#    folder = 'ships'
#    ship_local_paths = [os.path.join(folder, filename)
#        for (dirpath, dirnames, filenames) in os.walk(folder)
#        for filename in filenames]
#    ships_data = []
#    for ship_local_path in ship_local_paths:
#        with open(ship_local_path, 'r') as fid:
#            ship_src = fid.read().decode('utf8')
#        ship_data = get_ship_data(ship_src)
#        print ship_local_path, len(ship_data.items())
#        ships_data.append(ship_data)

    ships_data = unpickle_from_file('ships_data.pkl')
    points = []
    for ship_data in ships_data:
        length_key = "LOA (Length Overall):" 
        draft_key = "Draught:"
        if length_key not in ship_data.keys() or draft_key not in ship_data.keys():
            continue
        length = ship_data[length_key]
        draft = ship_data[draft_key]
        if length > 400 or draft > 30:
            continue
        points.append((length, draft))

    downscale = 3
    int_matrix = (np.vstack(points) / downscale).astype(np.uint64)
    length = int_matrix[:, 0]
    draft = int_matrix[:, 1]
    cdf = [[np.sum((length == j) & (draft == i)) for i in range(400 / downscale)]
        for j in range(30 / downscale)]
    cdf = np.array(cdf)

    plt.close('all')
    plt.figure('image ' + str(cdf.shape))
    plt.imshow(cdf, interpolation='nearest')

    plt.figure('Scatter plot')
    x, y = zip(*points)
    plt.plot(x, y, 'r.')
    plt.xlabel('Length (m)')
    plt.ylabel('Draft (m)')
    plt.show()


#    # Downloads all the ship pages from downloaded catalog pages
#    folder = 'C'
#    for alphabet in list('DE'):
#        catalog_files = [os.path.join(alphabet, filename)
#            for (dirpath, dirnames, filenames) in os.walk(alphabet)
#            for filename in filenames]
#        for catalog_file in catalog_files:
#            with open(catalog_file , 'r') as fid:
#                catalog_src = fid.read().decode('utf8')
#            download_ships_from_catalog(catalog_src, verbose=True)
#


##    ship_links = [x for src in catalog_sources for link in get_ship_links]
##    print files

#    foo = 'http://www.marinetraffic.com/ais/datasheet.aspx?datasource=SHIPS_CURRENT&alpha='
#    alphabets = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#    seed_URL = 'http://www.marinetraffic.com/ais/datasheet.aspx?datasource=SHIPS_CURRENT&alpha=C&mode='
#
#    # Goes through all catalogs of all beginning alphabets
#    next_URL = seed_URL
#    for alphabet in list(alphabets[4:]):
#        next_URL = re.sub('alpha=.', 'alpha=' + alphabet, seed_URL)
#        if not os.path.exists(alphabet):
#            os.mkdir(alphabet)
#
#        # Goes down the catalog of ships beginning with the same alphabet
#        while True:
#            print next_URL
#            src = get_src(next_URL)
#            download_ships_from_catalog(src, verbose=True)
#
##            page_no = get_page_no(src)
##            with open(os.path.join(alphabet, page_no), 'w') as fid:
##                fid.write(src.encode('utf8'))
#            leaf_URL = get_next_page(src)
#            if not leaf_URL:
#                break
#            next_URL = root_URL + leaf_URL


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
