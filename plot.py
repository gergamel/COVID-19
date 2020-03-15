#!/usr/bin/env python3
import sqlite3
DB_FILE="csse_covid_19.db"

import math
import datetime as dt
import numpy as np
import csv
from collections import namedtuple

#db_file=':memory:'

def todate(str_date):
    return dt.datetime.strptime(str_date,'%m/%d/%y')

def toint(str_int):
    try:
        return int(str_int)
    except ValueError:
        pass
    return None

Location=namedtuple("location", ('id','state','region','lat','long'))
Data=namedtuple("data", ('id','location_id', 'date', 'cases'))
TimeSeries=namedtuple("Series",('t','y'))
NamedTimeSeries=namedtuple("NamedData",('name','t','y'))

def to_location(row):
     return Location(id=row[0],state=row[1],region=row[2],lat=row[3],long=row[4])

def to_data(row):
     return Data(id=row[0],location_id=row[1],date=dt.datetime.fromtimestamp(row[2]),lat=row[3],long=row[4])

def to_time_series(row):
     return TimeSeries(t=dt.datetime.fromtimestamp(row[0]),y=row[1])

class Session():
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.cursor()
    def flush(self):
        self.c.execute('''DROP TABLE IF EXISTS data;''')
        self.c.execute('''DROP TABLE IF EXISTS location;''')
        self.conn.commit()
        self.c.execute('''CREATE TABLE IF NOT EXISTS location (id INTEGER NOT NULL PRIMARY KEY, state text, region text, lat real, long real);''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS data (location_id, date integer, cases integer, deaths integer);''')
    def import_data(self):
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
            self.c.execute('INSERT INTO location (state, region, lat, long) VALUES (?,?,?,?)',line[0:4])
            #c.execute('INSERT INTO location (state, region, lat, long) VALUES (?,?,?,?)',line[0:4])
            loc_id=self.c.lastrowid
            n=0
            for v in map(toint,line[4:]):
                self.c.execute('INSERT INTO data (location_id, date, cases) VALUES (?,?,?)',(loc_id,int(date_row[n].timestamp()),v))
                n+=1
        f.close()
        self.conn.commit()
    def execute(self,sql,**kwargs):
        self.c.execute(sql,**kwargs)
    def commit(self):
        self.conn.commit()
    def close(self):
        self.conn.close()
    def get_locations(self):
        return map(to_location,self.c.execute("SELECT * FROM location ORDER BY region,state;"))
    def get_regions(self):
        return self.c.execute("SELECT DISTINCT region FROM location ORDER BY region;")
    def get_region_totals(self):
        return self.c.execute("""SELECT l.region, MAX(d.cases) AS cases
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        GROUP BY l.region ORDER BY cases;""")
    def get_series(self,state,x_offset=dt.datetime(2020, 2, 20)):
        offset_ts=int(x_offset.timestamp()/86400)
        sql_str=f"""SELECT d.date, d.cases
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.state='{state}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.floor((np.array(dates, dtype=np.float)/86400) - offset_ts)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=state,t=t,y=y)
    def get_region_total_series(self,region,x_offset=dt.datetime(2020, 2, 20)):
        offset_ts=int(x_offset.timestamp()/86400)
        sql_str=f"""SELECT d.date, SUM(d.cases) AS cases
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.region='{region}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.floor((np.array(dates, dtype=np.float)/86400) - offset_ts)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=region,t=t,y=y)

c=Session()
c.flush()
c.import_data()
c.close()

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

##########################################################################################
# MATPLOTLIB HELPER FUNCTIONS
##########################################################################################

def setup_xaxis(axis,label,limits,tick_spacing,color='black'):
    axis.set_xlabel(label,color=color)
    axis.set_xticks(np.arange(limits[0],limits[1]+0.01, tick_spacing[0]))
    axis.set_xticks(np.arange(limits[0],limits[1]+0.01, tick_spacing[1]), minor=True)
    axis.tick_params(axis='y',which='both',labelcolor=color)
    axis.grid(axis='x',which='major',visible=True,color=color,alpha=0.5,linestyle=':')
    axis.grid(axis='x',which='minor',visible=True,color=color,alpha=0.25,linestyle=':')
    #axis.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
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

##########################################################################################
# DATA MODEL
##########################################################################################

#c.execute('''CREATE TABLE IF NOT EXISTS location (id INTEGER NOT NULL PRIMARY KEY, state text, region text, lat real, long real);''')
#c.execute('''CREATE TABLE IF NOT EXISTS data (location_id, date integer, cases integer, deaths integer);''')

##########################################################################################

#conn = sqlite3.connect(DB_FILE)
#c = conn.cursor()
c=Session()
for r in c.get_region_totals():
    print(r)

plot_regions=(
'Japan',
'Singapore',
'Korea, South',
'France',
'Spain',
'United Kingdom',
'Italy',
'US',
'Australia',
)

#fig, ax = plt.subplots(1,1)
ax = plt.gca()
lines=[]

data = []
data.append(c.get_series('Hong Kong'))
for r in plot_regions:
    data.append(c.get_region_total_series(r))

c.close()
tmax=0
ymax=0
for s in data:
    stmax=np.nanmax(s.t)
    if stmax>tmax: tmax=stmax
    symax=10000*np.ceil(np.nanmax(s.y)/10000)
    if symax>ymax: ymax=symax
    ln,=ax.semilogy(s.t,s.y)
    ln.set_label(f'{s.name}')
    lines.append(ln)

setup_xaxis(ax,"Days Since 20-Feb",[0,tmax],[10,1],color='black')
setup_logyaxis(ax,"Confirmed Cases",[100,ymax],[ymax/10,ymax/20],color='black')
ax.legend(lines, [l.get_label() for l in lines])
plt.title("John-Hopkins CSSE COVID-19 Data")
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