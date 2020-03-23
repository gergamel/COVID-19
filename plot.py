#!/usr/bin/env python3
import datetime as dt
import numpy as np
import covid
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

def setup_taxis(axis,label,limits,tick_spacing,color='black'):
    axis.set_xlabel(label,color=color)
    #axis.set_xticks(np.arange(limits[0],limits[1], tick_spacing[0]))
    t=limits[0]
    tticks=[t]
    while t<limits[1]:
        t+=dt.timedelta(days=1)
        tticks.append(t)
    axis.set_xticks(tticks, minor=True)
    #axis.tick_params(axis='y',which='both',labelcolor=color)
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

c=covid.Session()

for r in c.region_total_cases():
    print(r)

plot_regions=(
'Italy',
'Germany',
'Spain',
'US',
'France',
'Korea, South',
'United Kingdom',
#'Canada',
#'Japan',
'Australia',
#'Singapore',
)

plot_colours={
'Italy':'royalblue',
'Spain':'y',
'Germany':'magenta',
'France':'olive',
'Korea, South':'lightsteelblue',
'Singapore':'tan',
'Japan':'lightpink',
'United Kingdom':'blueviolet',
'US':'saddlebrown',
'Canada':'violet',
'Australia':'green',
'Western Australia':'lime',
'Hong Kong':'aquamarine'
}

fit_regions=(
'Singapore',
'Japan',
'United Kingdom',
'US',
'Canada',
'Germany',
'France',
'Spain',
'Australia',
#'Hong Kong',
'Western Australia',
)

beds_per_1000={
    "Italy":3.2,
    "Spain":3,
    "Germany":8,
    "France":6,
    "Korea, South":12.3,
    "US":2.8,
    "United Kingdom":2.5,
    "Japan":13.1,
    "Canada":2.5,
    "Australia":3.8
}
population={
    "Italy":60480000.00,
    "Spain":46660000.00,
    "Germany":82790000.00,
    "France":66990000.00,
    "Korea, South":51470000.00,
    "US":327200000.00,
    "United Kingdom":66440000.00,
    "Japan":126800000.00,
    "Canada":37590000.00,
    "Australia":24600000.00
}
beds={
    "Italy":193536.00,
    "Spain":139980.00,
    "Germany":662320.00,
    "France":401940.00,
    "Korea, South":633081.00,
    "US":916160.00,
    "United Kingdom":166100.00,
    "Japan":1661080.00,
    "Canada":93975.00,
    "Australia":93480.00
}

case_data = []
for r in plot_regions:
    case_data.append(c.region_case_series(r))
#case_data.append(c.case_series('Hong Kong'))
#case_data.append(c.case_series('Western Australia'))

death_data = []
for r in plot_regions:
    death_data.append(c.region_death_series(r))
#death_data.append(c.death_series('Hong Kong'))
#death_data.append(c.death_series('Western Australia'))
"""
drate_data = []
for r in plot_regions:
    drate_data.append(c.region_drate_series(r))
drate_data.append(c.drate_series('Hong Kong'))
"""
active_data = []
for r in plot_regions:
    active_data.append(c.region_active_series(r))
#active_data.append(c.active_series('Hong Kong'))
#active_data.append(c.active_series('Western Australia'))

"""
recovered_data = []
for r in plot_regions:
    recovered_data.append(c.region_recovered_series(r))
#recovered_data.append(c.recovered_series('Hong Kong'))
recovered_data.append(c.region_recovered_series('Western Australia'))
"""

c.close()
##########################################################################################
#fig1, ax = plt.subplots(2,1)
fig1, ax1 = plt.subplots(figsize=(12, 6), dpi=150)
#fig2, ax2 = plt.subplots(figsize=(12, 6), dpi=150)
lines=[]
fit_lines=[]
n=0
tmax=0
ymax=0
lookahead_days=21.0
lookahead=lookahead_days*86400.0

tmin=dt.datetime(2020, 2, 20)
tmin_ts=float(dt.datetime(2020, 2, 20).timestamp())
tmax_ts=0
for n in range(0,len(active_data)):
    s=active_data[n]
    tsmax=s.t[-1]+lookahead+86400.0
    if tsmax>tmax_ts:tmax_ts=tsmax
    n+=1
tmax=dt.datetime.fromtimestamp(int(tmax_ts))

n=0
for n in range(0,len(active_data)):
    s=case_data[n]
    drate=100.0*(death_data[n].y[-1]/case_data[n].y[-1])
    max_cases=np.nanmax(s.y)
    t=[]
    for tval in s.t:
        t.append(dt.datetime.fromtimestamp(int(tval)))
    ln,=ax1.semilogy(t,s.y,'-',color=plot_colours[s.name])
    ln.set_label(f'{s.name} ({max_cases:.0f}, {drate:.1f}%)')
    lines.append(ln)
    if s.name in fit_regions:
        # Generate look-ahead data based on exponenetial best fit
        if s.name=='Western Australia':
            idx=np.argwhere(s.y > 10.0)
        else:
            idx=np.argwhere(s.y > 100.0)
        t_fit=s.t[idx[0][0]:]-tmin_ts
        y_fit=np.log(s.y[idx[0][0]:])
        curve_fit=np.polyfit(t_fit,y_fit,1)
        t_fit=np.arange(s.t[0],tmax_ts,86400.0)-tmin_ts # Generate t axis with look-ahead 10 days
        y_fit = np.exp(curve_fit[1]) * np.exp(curve_fit[0]*t_fit)
        #print(t_fit,y_fit)
        t=[]
        for tval in t_fit:
            t.append(dt.datetime.fromtimestamp(int(tval+tmin_ts)))
            #if tval>tmax: tmax=tval
        fit_ln,=ax1.semilogy(t,y_fit,':',color=plot_colours[s.name])
        fit_lines.append(fit_ln)
    n+=1
#tmax=35
ymax=100000
tlims=[dt.datetime(2020, 2, 20),tmax]
setup_taxis(ax1,"",tlims,[5,1],color='black')
setup_logyaxis(ax1,"Active Cases",[100,ymax],[ymax/10,ymax/20],color='black')
ax1.legend(lines, [l.get_label() for l in lines])
now=dt.datetime.now()
ax1.set_title(f"COVID-19 Active Cases (latest count, fatality rate)\nGenerated: {now.strftime('%d-%b-%Y')}\nSRC: https://github.com/CSSEGISandData/COVID-19")
#ax1.title.set_url = 'https://github.com/CSSEGISandData/COVID-19'
#'https://data.oecd.org/healtheqt/hospital-beds.htm'

"""
lines=[]
n=0
for n in range(0,len(active_data)):
    s=active_data[n]
    if s.name not in beds.keys():continue
    t=[]
    for tval in s.t:
        t.append(dt.datetime.fromtimestamp(int(tval)))
    ln,=ax2.plot(t,100.0*s.y/beds[s.name],'-',color=plot_colours[s.name])
    ln.set_label(f'{s.name}')
    lines.append(ln)
    n+=1
n=0
"""
"""
for n in range(0,len(drate_data)):
    s=drate_data[n]
    if s.name not in beds.keys():continue
    t=[]
    for tval in s.t:
        t.append(dt.datetime.fromtimestamp(int(tval)))
    ln,=ax2.plot(t,s.y,':',color=plot_colours[s.name])
    ln.set_label(f'{s.name}')
    n+=1
"""
"""
tlims=[dt.datetime(2020, 2, 20),tmax]
setup_taxis(ax2,"Date",tlims,[5,1],color='black')
setup_yaxis(ax2,"Active Cases/Hospital Beds(%)",[0,20],[1,5],color='black')
ax2.legend(lines, [l.get_label() for l in lines])
ax2.set_title(f"Active Cases as a proportion of Available Hospital Beds (data age varies from 2015-2018)\nSRC: https://data.oecd.org/healtheqt/hospital-beds.htm")
"""
plt.show()
##########################################################################################
"""
fig1, ax = plt.subplots()
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
