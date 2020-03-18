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
Data=namedtuple("data", ('id','location_id', 'date', 'cases', 'deaths'))
TimeSeries=namedtuple("Series",('t','y'))
NamedTimeSeries=namedtuple("NamedData",('name','t','y'))

def to_location(row):
     return Location(id=row[0],state=row[1],region=row[2],lat=row[3],long=row[4])

def to_data(row):
     return Data(id=row[0],location_id=row[1],date=dt.datetime.fromtimestamp(row[2]),cases=row[3],deaths=row[4])

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
        self.c.execute('''CREATE TABLE IF NOT EXISTS location (id INTEGER NOT NULL PRIMARY KEY, state text NOT NULL, region text NOT NULL, lat real, long real);''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS data (id INTEGER NOT NULL PRIMARY KEY, location_id NOT NULL, date integer NOT NULL, cases integer, deaths integer);''')
    def import_data(self):
        # Confirmed cases
        f=open("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv",'r')
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
                self.c.execute('INSERT INTO data (location_id, date, cases, deaths) VALUES (?,?,?,?)',(loc_id,int(date_row[n].timestamp()),v,None))
                n+=1
        f.close()
        self.conn.commit()
    def find_location(self,state,region):
        rows=self.c.execute('SELECT * from location WHERE state=? AND region=?',(state,region))
        result=list(rows)
        if len(result)!=1:
            return None
        return to_location(result[0])
    def find_data(self,loc_id,date):
        rows=self.c.execute('SELECT id,location_id,date,cases,deaths from data WHERE location_id=? AND date=?',(loc_id,date))
        result=list(rows)
        if len(result)!=1:
            return None
        return to_data(result[0])
    def update_data(self):
        """
        f=open("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv",'r')
        rdr=csv.reader(f, delimiter=',')
        date_row=list(map(todate,rdr.__next__()[4:]))
        for line in rdr:
            loc=self.find_location(line[0],line[1])
            if loc is None:
                print(f"MISSING LOCATION: {line}")
                continue
            print(loc)
            n=0
            for v in map(toint,line[4:]):
                d=self.find_data(loc.id,int(date_row[n].timestamp()))
                if d is None:
                    self.c.execute('INSERT INTO data (location_id, date, cases) VALUES (?,?,?)',(loc.id,int(date_row[n].timestamp()),v))
                else:
                    self.c.execute('UPDATE data SET cases=? WHERE id=?',(v,d.id))
                n+=1
        self.conn.commit()
        f.close()
        """
        f=open("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv",'r')
        rdr=csv.reader(f, delimiter=',')
        date_row=list(map(todate,rdr.__next__()[4:]))
        for line in rdr:
            loc=self.find_location(line[0],line[1])
            if loc is None:
                print(f"MISSING LOCATION: {line}")
                continue
            print(loc)
            n=0
            for v in map(toint,line[4:]):
                d=self.find_data(loc.id,int(date_row[n].timestamp()))
                if d is None:
                    self.c.execute('INSERT INTO data (location_id, date, deaths) VALUES (?,?,?)',(loc.id,int(date_row[n].timestamp()),v))
                else:
                    self.c.execute('UPDATE data SET deaths=? WHERE id=?',(v,d.id))
                n+=1
        self.conn.commit()
        f.close()
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
    def region_total_cases(self):
        return self.c.execute("""SELECT l.region, MAX(d.cases) AS cases, MAX(d.deaths) as deaths
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        GROUP BY l.region ORDER BY cases;""")
    def case_series(self,state,x_offset=dt.datetime(2020, 2, 20)):
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
    def region_case_series(self,region,x_offset=dt.datetime(2020, 2, 20)):
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
    def death_series(self,state,x_offset=dt.datetime(2020, 2, 20)):
        offset_ts=int(x_offset.timestamp()/86400)
        sql_str=f"""SELECT d.date, d.deaths
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.state='{state}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.floor((np.array(dates, dtype=np.float)/86400) - offset_ts)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=state,t=t,y=y)
    def region_death_series(self,region,x_offset=dt.datetime(2020, 2, 20)):
        offset_ts=int(x_offset.timestamp()/86400)
        sql_str=f"""SELECT d.date, SUM(d.deaths) AS deaths
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.region='{region}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.floor((np.array(dates, dtype=np.float)/86400) - offset_ts)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=region,t=t,y=y)

c=Session()
#c.flush()
#c.import_data()
#c.update_data()
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

from matplotlib.ticker import StrMethodFormatter, NullFormatter
#ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.0f}'))
#ax.yaxis.set_minor_formatter(NullFormatter())

def setup_logyaxis(axis,label,limits,tick_spacing,color='black'):
    axis.set_ylabel(label,color=color)
    #axis.set_yticks(np.arange(limits[0],limits[1], tick_spacing[0]))
    #axis.set_yticks(np.arange(limits[0],limits[1], tick_spacing[1]), minor=True)
    #axis.tick_params(axis='y',which='both',labelcolor=color)
    axis.grid(axis='y',which='major',visible=True,color=color,alpha=0.5,linestyle='-')
    axis.grid(axis='y',which='minor',visible=True,color=color,alpha=0.25,linestyle='-')
    axis.yaxis.set_major_formatter(StrMethodFormatter('{x:.0f}'))
    axis.yaxis.set_minor_formatter(NullFormatter())
    axis.set_ylim(limits)

c=Session()

for r in c.region_total_cases():
    print(r)

plot_regions=(
'Singapore',
'Australia',
'Japan',
'Netherlands',
'United Kingdom',
'US',
'Germany',
'Korea, South',
'Italy',
)

case_data = []
case_data.append(c.case_series('Hong Kong'))
for r in plot_regions:
    case_data.append(c.region_case_series(r))

death_data = []
death_data.append(c.death_series('Hong Kong'))
for r in plot_regions:
    death_data.append(c.region_death_series(r))

c.close()
##########################################################################################
#fig, ax = plt.subplots(2,1)
fig, ax = plt.subplots(figsize=(11, 6), dpi=100)
lines=[]
tmax=0
ymax=0
for n in range(0,len(case_data)):
    s=case_data[n]
    drate=100.0*(death_data[n].y[-1]/case_data[n].y[-1])
    stmax=np.nanmax(s.t)
    if stmax>tmax: tmax=stmax
    max_cases=np.nanmax(s.y)
    symax=10000*np.ceil(max_cases/10000)
    if symax>ymax: ymax=symax
    ln,=ax.semilogy(s.t,s.y)
    ln.set_label(f'{s.name} ({max_cases:.0f}, {drate:.1f}%)')
    lines.append(ln)
#tmax=35
setup_xaxis(ax,"Days Since 20-Feb",[0,tmax],[5,1],color='black')
setup_logyaxis(ax,"Confirmed Cases",[100,ymax],[ymax/10,ymax/20],color='black')
ax.legend(lines, [l.get_label() for l in lines])
plt.title("COVID-19 Cumulative Cases (latest count, fatality rate)")
plt.show()
##########################################################################################
"""
fig, ax = plt.subplots()
lines=[]
tmax=0
ymax=0
for n in range(0,len(case_data)):
    t=case_data[n].t
    y=100.0*np.divide(death_data[n].y,case_data[n].y)
    stmax=np.nanmax(t)
    if stmax>tmax: tmax=stmax
    symax=np.ceil(np.nanmax(y))
    if symax>ymax: ymax=symax
    ln,=ax.plot(t,y)
    ln.set_label(f'{case_data[n].name} ({y[-1]:.1f}%)')
    lines.append(ln)
setup_xaxis(ax,"Days Since 20-Feb",[0,tmax],[10,1],color='black')
setup_yaxis(ax,"Death rate (%)",[0,ymax],[ymax/10,ymax/20],color='black')
ax.legend(lines, [l.get_label() for l in lines])
plt.title("John-Hopkins CSSE COVID-19 Data")
plt.show()
"""
exit(0)
