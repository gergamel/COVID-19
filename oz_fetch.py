
#!/usr/bin/env python3
import covid
import datetime as dt
import numpy as np
import requests
import urllib.request
import time
import bs4
import json
import re

case_data={
'Australian Capital Territory':0,
'New South Wales':0,
'Northern Territory':0,
'Queensland':0,
'South Australia':0,
'Tasmania':0,
'Victoria':0,
'Western Australia':0,
}

death_data={
'Australian Capital Territory':0,
'New South Wales':0,
'Northern Territory':0,
'Queensland':0,
'South Australia':0,
'Tasmania':0,
'Victoria':0,
'Western Australia':0,
}

url="https://infogram.com/1pe61w3qz65eqmfm60g2wll721tl16eq5wz"
"""
<script>
window.infographicData={
    "id":149194683,
    "type":0,
    "block_id":"23dbde13-9fdc-4c11-84e5-17372ce139d3",
    "theme_id":289,"user_id":6761376,
    "team_user_id":null,
    "path":"a438113b-879a-4b73-be53-dcad1ee24160",
    "title":"Transmission in each state",
    "description":"",
    "tags":"",
    ...
    "accessibility":{"enabled":true},
    "text":"\u003Cfont style=\"font-size: 24px\"\u003E\u003Cspan style=\"font-family:ubuntu;font-size: 24px;font-style: normal;font-weight: 500;text-align: left\"\u003ECOVID-19 in Australia\u003C\u002Fspan\u003E\u003C\u002Ffont\u003E","content_type":"text\u002Fhtml","title":"","shrink":null},{"type":"chart","chart_id":349276203,"object_id":"3166d247-baad-4ed2-a0ce-b432745b8ab8","chart_type_nr":19,
    "data":[
        [
            ["State","Cases","% of overall cases","Deaths","Confirmed local transmissions"],
            ["NSW","436","41%","5","63"],
            ["VIC","229","21%","0","2"],
            ["QLD","221","21%","1","4"],
            ["WA","90","8%","1","2"],
            ["SA","67","6%","0","6"],
            ["TAS","16","1%","0","0"],
            ["ACT","9","1%","0","1"],
            ["NT","4","0%","0","0"],
            ["","","","",""],
            ["Totals","1072","","7","78"]
        ]
    ],
    ...
    "indexStatus":true,"branding":{"colors":[],"fonts":[],"webfonts":[]}};</script>
"""
response = requests.get(url)
if response.status_code!=200:
    print(response.status_code)
    exit(0)
soup = bs4.BeautifulSoup(response.text, "html.parser")

keymap={
'ACT':'Australian Capital Territory',
'NSW':'New South Wales',
'VIC':'Northern Territory',
'QLD':'Queensland',
'SA':'South Australia',
'TAS':'Tasmania',
'VIC':'Victoria',
'WA':'Western Australia',
'NT':'Northern Territory',
}

#ts_element=soup.findAll('script')
for s in soup.findAll('script'):
    if "infographicData" in s.text:
        d=json.loads(s.text.replace(";","").split("=",1)[1])
        table=d['elements'][1]['data']
        for r in table[0]:
            if r[0] in keymap:
                k=keymap[r[0]]
                cases=r[1]
                deaths=r[4]
                case_data[k]=float(cases)
                death_data[k]=float(deaths)


fetch_date_str=dt.datetime.now().strftime('%Y-%m-%d')
fetch_date=dt.datetime.strptime(fetch_date_str,'%Y-%m-%d')

"""
url="https://www.health.gov.au/news/health-alerts/novel-coronavirus-2019-ncov-health-alert/coronavirus-covid-19-current-situation-and-case-numbers"
response = requests.get(url)
if response.status_code!=200:
    print(response.status_code)
    exit(0)
soup = bs4.BeautifulSoup(response.text, "html.parser")

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
"""

c=covid.Session()

for state in case_data.keys():
    s=c.case_series(state)
    last_ts=dt.datetime.fromtimestamp(int(s.t[-1]))
    last_date=last_ts.strftime('%d-%b')
    #new_date=fetch_date.strftime('%d-%b')
    #print(f'{k},{new_date},{data[k]} [{last_date},{s.y[-1]}]')
    if case_data[state]>s.y[-1]:
        location=c.find_state(state)
        c.new_data(location.id,fetch_date,case_data[state],death_data[state])
        print(f"Inserted new data record: {state},{fetch_date.strftime('%d-%b')},{case_data[state]},{death_data[state]} [Last {last_date},{s.y[-1]}]")
