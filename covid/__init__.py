#!/usr/bin/env python3
import sqlite3
import datetime as dt
import numpy as np
import csv
from collections import namedtuple

DB_FILE="csse_covid_19.db"
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
Data=namedtuple("data", ('id','location_id', 'date', 'cases', 'deaths', 'recovered'))
TimeSeries=namedtuple("Series",('t','y'))
NamedTimeSeries=namedtuple("NamedData",('name','t','y'))

def to_location(row):
     return Location(id=row[0],state=row[1],region=row[2],lat=row[3],long=row[4])

def to_data(row):
     return Data(id=row[0],location_id=row[1],date=dt.datetime.fromtimestamp(row[2]),cases=row[3],deaths=row[4],recovered=row[5])

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
        self.c.execute('''CREATE TABLE IF NOT EXISTS data (id INTEGER NOT NULL PRIMARY KEY, location_id NOT NULL, date int NOT NULL, cases integer, deaths integer, recovered integer);''')
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
                self.c.execute('INSERT INTO data (location_id, date, cases, deaths, recovered) VALUES (?,?,?,?,?)',(loc_id,int(date_row[n].timestamp()),v,None,None))
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
        rows=self.c.execute('SELECT id,location_id,date,cases,deaths,recovered from data WHERE location_id=? AND date=?',(loc_id,date))
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
        f=open("csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv",'r')
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
                    self.c.execute('INSERT INTO data (location_id, date, recovered) VALUES (?,?,?)',(loc.id,int(date_row[n].timestamp()),v))
                else:
                    self.c.execute('UPDATE data SET recovered=? WHERE id=?',(v,d.id))
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
        return self.c.execute("""SELECT l.region, MAX(d.cases) AS cases, MAX(d.deaths) as deaths, MAX(d.recovered) as recovered
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        GROUP BY l.region ORDER BY cases;""")
    def case_series(self,state):
        sql_str=f"""SELECT d.date, d.cases
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.state='{state}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.array(dates, dtype=np.float)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=state,t=t,y=y)
    def region_case_series(self,region):
        sql_str=f"""SELECT d.date, SUM(d.cases) AS cases
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.region='{region}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.array(dates, dtype=np.float)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=region,t=t,y=y)
    def death_series(self,state):
        sql_str=f"""SELECT d.date, d.deaths
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.state='{state}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.array(dates, dtype=np.float)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=state,t=t,y=y)
    def region_death_series(self,region):
        sql_str=f"""SELECT d.date, SUM(d.deaths) AS deaths
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.region='{region}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.array(dates, dtype=np.float)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=region,t=t,y=y)
    def recovered_series(self,state):
        sql_str=f"""SELECT d.date, d.recovered
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.state='{state}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.array(dates, dtype=np.float)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=state,t=t,y=y)
    def region_recovered_series(self,region):
        sql_str=f"""SELECT d.date, SUM(d.recovered) AS recovered
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.region='{region}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.array(dates, dtype=np.float)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=region,t=t,y=y)
    def active_series(self,state):
        sql_str=f"""SELECT d.date, (d.cases-d.recovered) as active
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.state='{state}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.array(dates, dtype=np.float)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=state,t=t,y=y)
    def region_active_series(self,region):
        sql_str=f"""SELECT d.date, (SUM(d.cases)-SUM(d.recovered)) AS active
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.region='{region}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.array(dates, dtype=np.float)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=region,t=t,y=y)
    def drate_series(self,state):
        sql_str=f"""SELECT d.date, (100.0*d.deaths/d.cases) as drate
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.state='{state}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.array(dates, dtype=np.float)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=state,t=t,y=y)
    def region_drate_series(self,region):
        sql_str=f"""SELECT d.date, (100.0*SUM(d.deaths)/SUM(d.cases)) as drate
        FROM data AS d JOIN location AS l ON d.location_id=l.id
        WHERE l.region='{region}'
        GROUP BY d.date;"""
        results=self.c.execute(sql_str)
        dates,cases=zip(*results)
        t=np.array(dates, dtype=np.float)
        y=np.array(cases, dtype=np.float)
        return NamedTimeSeries(name=region,t=t,y=y)
