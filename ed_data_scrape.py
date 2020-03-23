#!/usr/bin/env python3
import requests
import urllib.request
import bs4

url="ww2.health.wa.gov.au/Reports-and-publications/Emergency-Department-activity/Data?report=ed_activity_now"

response = requests.get(url)
if response.status_code!=200:
    print(response.status_code)
    exit(0)
soup = bs4.BeautifulSoup(response.text, "html.parser")