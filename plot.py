#!/usr/bin/env python3
import sqlite3
DB_FILE="csse_covid_19.db"

'''
Province/States,Country/Region,              WHO region,1/21/20,1/22/20,1/23/20,1/24/20,1/25/20,1/26/20,1/27/20,1/28/20,1/29/20,1/30/20,1/31/20,2/1/20,2/2/20,2/3/20,2/4/20,2/5/20,2/6/20,2/7/20,2/8/20,2/9/20,2/10/20,2/11/20,2/12/20,2/13/20,2/14/20,2/15/20,2/16/20,2/17/20,2/18/20,2/19/20,2/20/20,2/21/20,2/22/20,2/23/20,2/24/20,2/25/20,2/26/20,2/27/20,2/28/20,2/29/20,3/1/20,3/2/20,3/3/20
Confirmed,      Globally,                              ,282,314,581,846,1320,2014,2798,4593,6065,7818,9826,11953,14557,17391,20630,24554,28276,31481,34886,37558,40554,43103,45171,46997,49053,50580,51857,71429,73332,75204,75748,76769,77794,78811,79331,80239,81109,82294,83652,85403,87137,88948,90870
Confirmed,      Mainland China,  Western Pacific Region,278,309,571,830,1297,1985,2741,4537,5997,7736,9720,11821,14411,17238,20471,24363,28060,31211,34598,37251,40235,42708,44730,46550,48548,50054,51174,70635,72528,74280,74675,75569,76392,77042,77262,77780,78191,78630,78961,79394,79968,80174,80304
Confirmed,      Outside of China,                      ,4,5,10,16,23,29,57,56,68,82,106,132,146,153,159,191,216,270,288,307,319,395,441,447,505,526,683,794,804,924,1073,1200,1402,1769,2069,2459,2918,3664,4691,6009,7169,8774,10566
Suspected,      Mainland China,  Western Pacific Region,,,,,,,5794,6973,9239,12167,15238,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Severe,         Mainland China,  Western Pacific Region,,,,,,,461,976,1239,1370,1527,1795,2110,2296,2788,3219,3859,4821,6101,6188,6484,7333,8204,,,,,,,,,,,,,,,,,,,,
Deaths,         Mainland China,  Western Pacific Region,,,,,,,80,106,132,170,213,259,304,361,425,491,564,637,723,812,909,1017,1114,1260,1381,1524,1666,1772,1870,2006,2121,2239,2348,2445,2595,2666,2718,2747,2791,2838,2873,2915,2946
Hubei ,         China,           Western Pacific Region,258,270,375,375,,,,,,,,7153,9074,11177,13522,16678,19665,22112,24953,27100,29631,31728,33366,34874,51968,54406,56249,58182,59989,61682,62031,62662,63454,64084,64287,64786,65187,65596,65914,66337,66907,67103,67217
'''

import math
import datetime as dt
import numpy as np

def todate(str_date):
    return dt.datetime.strptime(str_date,'%m/%d/%y')

def toint(str_int):
    try:
        return int(str_int)
    except ValueError:
        pass
    return None

def import_data():
    import csv
    #db_file=':memory:'
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS data;''')
    c.execute('''DROP TABLE IF EXISTS location;''')
    conn.commit()
    c.execute('''CREATE TABLE IF NOT EXISTS location (id INTEGER NOT NULL PRIMARY KEY, state text, region text, lat real, long real);''')
    c.execute('''CREATE TABLE IF NOT EXISTS data (location_id, date integer, cases integer, deaths integer);''')

    conf_csv="csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
    f=open(conf_csv)
    r=csv.reader(f, delimiter=',')
    """
    Headers in the CSV are:
    0-Province/State
    1-Country/Region
    2-Lat
    3-Long
    4-1/22/20
    5-1/23/20
    etc...
    """
    date_row=list(map(todate,r.__next__()[4:]))
    for line in r:
        c.execute('INSERT INTO location (state, region, lat, long) VALUES (?,?,?,?)',line[0:4])
        #c.execute('INSERT INTO location (state, region, lat, long) VALUES (?,?,?,?)',line[0:4])
        loc_id=c.lastrowid
        n=0
        for v in map(toint,line[4:]):
            c.execute('INSERT INTO data (location_id, date, cases) VALUES (?,?,?)',(loc_id,int(date_row[n].timestamp()),v))
            n+=1
    f.close()
    conn.commit()
    conn.close()

import_data()

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import namedtuple

#c.execute('''CREATE TABLE IF NOT EXISTS location (id INTEGER NOT NULL PRIMARY KEY, state text, region text, lat real, long real);''')
#c.execute('''CREATE TABLE IF NOT EXISTS data (location_id, date integer, cases integer, deaths integer);''')

Location=namedtuple("location", ('id','state','region','lat','long'))
Data=namedtuple("data", ('id','location_id', 'date', 'cases'))
RegionData=namedtuple("RegionData",('date','cases'))

def row2location(row):
     return Location(id=row[0],state=row[1],region=row[2],lat=row[3],long=row[4])

def row2data(row):
     return Data(id=row[0],location_id=row[1],date=dt.datetime.fromtimestamp(row[2]),lat=row[3],long=row[4])

def row2regiondata(row):
     return RegionData(date=dt.datetime.fromtimestamp(row[0]),cases=row[1])

def get_locations(c):
    return map(row2region,c.execute("SELECT * FROM location;"))

def get_regions(c):
    return c.execute("SELECT DISTINCT region FROM location ORDER BY region;")

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
for r in get_regions(c):
    print(r)

region_data=list(map(row2regiondata,c.execute("""
SELECT d.date, SUM(d.cases) AS cases
FROM data AS d JOIN location AS l ON d.location_id=l.id
WHERE l.region='Australia'
GROUP BY d.date""")))
x0=dt.datetime(2020, 1, 22)

x=tuple(((r.date-x0).days for r in region_data))
y=tuple((r.cases for r in region_data))
print(x)
print(y)
c.close()

def setup_xaxis(axis,label,limits,tick_spacing,color='black'):
    axis.set_xlabel(label,color=color)
    axis.set_xticks(np.arange(limits[0],limits[1]+dt.timedelta(seconds=1), tick_spacing[0]))
    axis.set_xticks(np.arange(limits[0],limits[1]+dt.timedelta(seconds=1), tick_spacing[1]), minor=True)
    axis.tick_params(axis='y',which='both',labelcolor=color)
    axis.grid(axis='x',which='major',visible=True,color=color,alpha=0.5,linestyle=':')
    axis.grid(axis='x',which='minor',visible=True,color=color,alpha=0.25,linestyle=':')
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    axis.set_xlim(limits)

def setup_yaxis(axis,label,limits,tick_spacing,color='black'):
    axis.set_ylabel(label,color=color)
    axis.set_yticks(np.arange(limits[0],limits[1]+0.001, tick_spacing[0]))
    axis.set_yticks(np.arange(limits[0],limits[1]+0.001, tick_spacing[1]), minor=True)
    axis.tick_params(axis='y',which='both',labelcolor=color)
    axis.grid(axis='y',which='major',visible=True,color=color,alpha=0.5,linestyle=':')
    axis.grid(axis='y',which='minor',visible=True,color=color,alpha=0.25,linestyle=':')
    axis.set_ylim(limits)

def setup_logyaxis(axis,label,limits,tick_spacing,color='black'):
    axis.set_ylabel(label,color=color)
    #axis.set_yticks(np.arange(limits[0],limits[1]+0.001, tick_spacing[0]))
    #axis.set_yticks(np.arange(limits[0],limits[1]+0.001, tick_spacing[1]), minor=True)
    #axis.tick_params(axis='y',which='both',labelcolor=color)
    axis.grid(axis='y',which='major',visible=True,color=color,alpha=0.5,linestyle=':')
    axis.grid(axis='y',which='minor',visible=True,color=color,alpha=0.25,linestyle=':')
    axis.set_ylim(limits)

xlims=[min(x),max(x)]

fig, ax = plt.subplots(1,1)
lines=[]
ln,=ax[0].plot(x,y)
ln.set_label(f'Confirmed ({cname})')
lines.append(ln)
####
setup_xaxis(ax[0],"Date",xlims,[dt.timedelta(days=10),dt.timedelta(days=1)],color='black')
setup_yaxis(ax[0],"Growth (%)",[0,100],[10,2],color='black')
ax[0].legend(lines, [l.get_label() for l in lines])

plt.show()

exit(0)

"""
f=open('who_covid_19_situation_reports/who_covid_19_sit_rep_time_series/who_covid_19_sit_rep_time_series.csv')
r=csv.reader(f, delimiter=',')
t=list(map(todate,r.__next__()[3:]))            # Headings
conf_global=list(map(toint,r.__next__()[3:]))     # Confirmed cases - Globally
conf_china=list(map(toint,r.__next__()[3:]))      # Confirmed cases - Mainland China
conf_non_china=list(map(toint,r.__next__()[3:]))  # Confirmed cases - Outside of China
sus_china=list(map(toint,r.__next__()[3:]))       # Suspected cases - China
sev_china=list(map(toint,r.__next__()[3:]))       # Severe cases - China
deaths_china=list(map(toint,r.__next__()[3:]))    # Deaths - China
countries={}
country_delta={}
for line in r:
    if line[1]!="China":
        countries[line[1]]=list(map(toint,line[3:]))
        country_delta[line[1]]=[]
"""

conf_csv="csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
f=open(conf_csv)
r=csv.reader(f, delimiter=',')
conf_cases={}
conf_cases_offset={}
conf_delta={}
country_t={}
t2=list(map(todate,r.__next__()[4:]))            # Headings
global_cases=[0 for t in t2]

def accumulate_country(country):
    if line[1]==country:
        if country not in conf_cases:
            conf_cases[country]=[]
            for v in line[4:]:
                conf_cases[country].append(0)
        n=0
        for v in line[4:]:
            try:
                conf_cases[country][n]+=int(v)
            except ValueError:
                pass
            n+=1
        conf_delta[country]=[0 for x in conf_cases[country]]

acc_countries=["China","US","Australia"]
for line in r:
    #Province/State,Country/Region,Lat,Long,1/22/20,etc...
    if line[1] not in acc_countries:
        conf_cases[line[1]]=list(map(toint,line[4:]))
        conf_delta[line[1]]=[0 for x in conf_cases[line[1]]]
    else:
        accumulate_country("China")
        accumulate_country("US")
        accumulate_country("Australia")
f.close()

def offset_t(t,offset):
    result = t
    n=0
    for tval in result:
        result[n]=tval-offset
        n+=1
    return result

for k,v in conf_cases.items():
    n=0
    for val in v:
        if val == None:
            conf_delta[k][n]=0.0
        else:
            if k not in conf_cases_offset:
                if int(val) >= 100.0:
                    conf_cases_offset[k]=t2[n]
                    country_t=offset_t(t2,t2[n])
            global_cases[n]+=int(val)
            delta = 0.0
            prev=conf_cases[k][n-1]
            if prev!=None and prev>=20.0:
                delta = 100.0*(val - prev)/prev
            conf_delta[k][n]=delta
        n+=1

#print(conf_cases_offset)

"""
deaths_csv="csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
for k,count in countries.items():
    n=0
    for v in count:
        if v == None:
            country_delta[k].append(None)
        else:
            delta = None
            prev=countries[k][n-1]
            if prev!=None:
                delta = 100.0*(v - prev)/prev
            country_delta[k].append(delta)
        n+=1
f.close()
"""

def setup_xaxis(axis,label,limits,tick_spacing,color='black'):
    axis.set_xlabel(label,color=color)
    axis.set_xticks(np.arange(limits[0],limits[1]+dt.timedelta(seconds=1), tick_spacing[0]))
    axis.set_xticks(np.arange(limits[0],limits[1]+dt.timedelta(seconds=1), tick_spacing[1]), minor=True)
    axis.tick_params(axis='y',which='both',labelcolor=color)
    axis.grid(axis='x',which='major',visible=True,color=color,alpha=0.5,linestyle=':')
    axis.grid(axis='x',which='minor',visible=True,color=color,alpha=0.25,linestyle=':')
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    axis.set_xlim(limits)

def setup_yaxis(axis,label,limits,tick_spacing,color='black'):
    axis.set_ylabel(label,color=color)
    axis.set_yticks(np.arange(limits[0],limits[1]+0.001, tick_spacing[0]))
    axis.set_yticks(np.arange(limits[0],limits[1]+0.001, tick_spacing[1]), minor=True)
    axis.tick_params(axis='y',which='both',labelcolor=color)
    axis.grid(axis='y',which='major',visible=True,color=color,alpha=0.5,linestyle=':')
    axis.grid(axis='y',which='minor',visible=True,color=color,alpha=0.25,linestyle=':')
    axis.set_ylim(limits)

def setup_logyaxis(axis,label,limits,tick_spacing,color='black'):
    axis.set_ylabel(label,color=color)
    #axis.set_yticks(np.arange(limits[0],limits[1]+0.001, tick_spacing[0]))
    #axis.set_yticks(np.arange(limits[0],limits[1]+0.001, tick_spacing[1]), minor=True)
    #axis.tick_params(axis='y',which='both',labelcolor=color)
    axis.grid(axis='y',which='major',visible=True,color=color,alpha=0.5,linestyle=':')
    axis.grid(axis='y',which='minor',visible=True,color=color,alpha=0.25,linestyle=':')
    axis.set_ylim(limits)

xlims=[min(t2),max(t2)]

fig, ax = plt.subplots(2,1)
"""
lines=[]
####
ln,=ax[0].plot(t2,global_cases)
ln.set_label('Confirmed (Global)')
lines.append(ln)
####
ln,=ax[0].plot(t2,conf_cases["China"])
ln.set_label('Confirmed (China)')
lines.append(ln)
####
y_max=10000*math.ceil(max(global_cases)/10000)
setup_xaxis(ax[0],"Date",xlims,[dt.timedelta(days=10),dt.timedelta(days=1)],color='black')
setup_yaxis(ax[0],"Count",[0,y_max],[10000,5000],color='black')
ax[0].legend(lines, [l.get_label() for l in lines])
"""
countries=["Korea, South","Italy","Australia","Iran","Germany","France"]

lines=[]
y_max=0
for cname in countries:
    ln,=ax[0].semilogy(country_t[cname],conf_cases[cname])
    ln.set_label(f'Confirmed ({cname})')
    lines.append(ln)
    new_y_max=1000*math.ceil(max(conf_cases[cname])/1000)
    if new_y_max > y_max: y_max=new_y_max
####
setup_xaxis(ax[0],"Date",xlims,[dt.timedelta(days=10),dt.timedelta(days=1)],color='black')
setup_logyaxis(ax[0],"Count",[0,y_max],[y_max/10,y_max/50],color='black')
ax[0].legend(lines, [l.get_label() for l in lines])

lines=[]
for cname in countries:
    ln,=ax[1].plot(t2,conf_delta[cname])
    ln.set_label(f'Confirmed ({cname})')
    lines.append(ln)
####
setup_xaxis(ax[1],"Date",xlims,[dt.timedelta(days=10),dt.timedelta(days=1)],color='black')
setup_yaxis(ax[1],"Growth (%)",[0,100],[10,2],color='black')
ax[1].legend(lines, [l.get_label() for l in lines])

plt.show()