
#!/usr/bin/env python3
import covid
import datetime as dt
import numpy as np
import requests
import urllib.request
import time
import bs4
import re

url="https://www.health.gov.au/news/health-alerts/novel-coronavirus-2019-ncov-health-alert/coronavirus-covid-19-current-situation-and-case-numbers"


response = requests.get(url)
if response.status_code!=200:
    print(response.status_code)
    exit(0)

soup = bs4.BeautifulSoup(response.text, "html.parser")

data={
'Australian Capital Territory':0,
'New South Wales':0,
'Northern Territory':0,
'Queensland':0,
'South Australia':0,
'Tasmania':0,
'Victoria':0,
'Western Australia':0,
}

#<p class="au-callout">As at 6.30am on 20 March 2020, there have been 709 <strong>confirmed cases</strong> of COVID-19 in Australia. There have been 144 new cases since 6.30am yesterday. </p>
ts_element=soup.find('p',{'class':"au-callout"}).next.replace(u'\xa0',' ')
ts_re=re.compile('As at .+ on (\d\d) (\w+) (\d\d\d\d)')
m=ts_re.match(ts_element)
if m is None:
    print(f"Failed to find date in: {ts_element}")
    exit(0)
datestring=f"{m.groups()[0]} {m.groups()[1]} {m.groups()[2]}"
new_fetch_date=dt.datetime.strptime(datestring,"%d %B %Y")

tables=soup.findAll('tbody')
for table in tables:
    rows=table.findAll('tr')
    for row in rows:
        cells=row.findAll('td')
        k=cells[0]
        v=cells[1]
        for c in k.children:
            if c=='\n':
                continue
            c1=c
        for c in v.children:
            if c=='\n':
                continue
            c2=c
        while type(c1) != bs4.element.NavigableString:
            c1=c1.next
        while type(c2) != bs4.element.NavigableString:
            c2=c2.next
        if c1 in data:
            data[str(c1)]=int(str(c2))

c=covid.Session()

case_data = []
for k in data.keys():
    s=c.case_series(k)
    last_ts=dt.datetime.fromtimestamp(int(s.t[-1]))
    last_date=last_ts.strftime('%d-%b')
    new_date=new_fetch_date.strftime('%d-%b')
    print(f'{k},{new_date},{data[k]} [{last_date},{s.y[-1]}]')