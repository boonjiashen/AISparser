"""Parses marinetraffic.com for AIS data"""
import urllib2
from bs4 import BeautifulSoup

URL = "http://www.marinetraffic.com/ais/shipdetails.aspx?imo=9524451"
import requests
URL = "http://www.marinetraffic.com/ais/shipdetails.aspx"
payload = {'imo': "9524451"}
src = requests.get(URL, params=payload).text

fields = """
LOA (Length Overall)
Beam
Draft (max)
""".strip().splitlines()
soup = BeautifulSoup(src)
data = {}
for field in fields:
    tags = [tag for tag in soup.find_all('b') if tag.string.find(field) != -1]
    assert len(tags) == 1
    value = float(tags[0].nextSibling.string)
    data[field] = value
print data

