#!/usr/bin/env python3
import covid
import datetime as dt
import numpy as np

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
    minor_ticks=[t]
    while t<limits[1]:
        t+=dt.timedelta(days=1)
        minor_ticks.append(t)
    t=limits[0]
    major_ticks=[t]
    while t<limits[1]:
        t+=dt.timedelta(days=7)
        major_ticks.append(t)
    axis.set_xticks(major_ticks)
    axis.set_xticks(minor_ticks, minor=True)
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

wa_only=True
t0_0=int(dt.datetime(2020,3,12).timestamp())
t0_1=int(dt.datetime(2020,3,18).timestamp())

for r in c.region_total_cases():
    print(r)

plot_regions=(
#'Australia',
#'New Zealand',
)
if wa_only:
    plot_states=(
        'Western Australia',
    )
    fit_regions=(
    'Western Australia',
    )
else:
    plot_states=(
    'New South Wales',
    'Queensland',
    'Victoria',
    'South Australia',
    'Western Australia',
    'Northern Territory',
    'Australian Capital Territory',
    'Tasmania',
    )
    fit_regions=(
    #'Australia',
    'New South Wales',
    'Queensland',
    'Victoria',
    'South Australia',
    'Western Australia',
    'Northern Territory',
    'Australian Capital Territory',
    'Tasmania',
    #'New Zealand',
    )
plot_colours={
'Italy':'royalblue',
'Korea, South':'lightsteelblue',
'Australia':'red',
'New Zealand':'y',
'Australian Capital Territory':'magenta',
'Northern Territory':'lightpink',
'Tasmania':'blueviolet',
'New South Wales':'saddlebrown',
'Queensland':'violet',
'Victoria':'aquamarine',
'South Australia':'yellow',
'Western Australia':'royalblue',
}
#SRC: ANZICS Centre for Outcome and Resource Evaluation Report 2018
icu_beds={
    "Australia":2229,
    "New Zealand":251,
    "Victoria":476,
    "Tasmania":50,
    "New South Wales":874,
    "Queensland":413,
    "South Australia":188,
    "Western Australia":162,
    "Northern Territory":22,
    "Australian Capital Territory":44,
}
max_active_cases={}
for k,v in icu_beds.items():
    max_active_cases[k]=v/0.05
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
for r in plot_states:
    case_data.append(c.case_series(r))

death_data = []
for r in plot_regions:
    death_data.append(c.region_death_series(r))
for r in plot_states:
    death_data.append(c.death_series(r))
"""
drate_data = []
for r in plot_regions:
    drate_data.append(c.region_drate_series(r))
drate_data.append(c.drate_series('Hong Kong'))
"""
active_data = []
for r in plot_regions:
    active_data.append(c.region_active_series(r))
for r in plot_states:
    active_data.append(c.active_series(r))

"""
recovered_data = []
for r in plot_regions:
    recovered_data.append(c.region_recovered_series(r))
#recovered_data.append(c.recovered_series('Hong Kong'))
recovered_data.append(c.region_recovered_series('Western Australia'))
"""

tmin=dt.datetime(2020, 3, 1)
tmin_ts=float(dt.datetime(2020, 3, 1).timestamp())
tmax_ts=0
lookahead_days=28.0
lookahead=lookahead_days*86400.0
for n in range(0,len(active_data)):
    s=active_data[n]
    tsmax=s.t[-1]+lookahead+86400.0
    if tsmax>tmax_ts:tmax_ts=tsmax
    n+=1
tmax=dt.datetime.fromtimestamp(int(tmax_ts))

fit_data = {}
tmax=0
for n in range(0,len(active_data)):
    #s=active_data[n]
    s=case_data[n]
    if s.name in fit_regions:
        # Generate look-ahead data based on exponenetial best fit
        idx=np.argwhere(s.t >= t0_0)
        t_fit=s.t[idx[0][0]:]-tmin_ts
        #t0=int(dt.datetime(2020,3,19).timestamp())
        y_fit=np.log(s.y[idx[0][0]:])
        curve_fit=np.polyfit(t_fit,y_fit,1)
        t_fit=np.arange(t0_0,tmax_ts,86400.0)-tmin_ts # Generate t axis with look-ahead 10 days
        y_fit = np.exp(curve_fit[1]) * np.exp(curve_fit[0]*t_fit)
        #print(t_fit,y_fit)
        t=[]
        for tval in t_fit:
            t.append(dt.datetime.fromtimestamp(int(tval+tmin_ts)))
            if tval>tmax: tmax=tval
        #fit_ln,=ax1.semilogy(t,y_fit,':',color=plot_colours[s.name])
        #fit_lines.append(fit_ln)
        fit_data[s.name]=[t,y_fit]

fit2_data = {}
tmax=0
for n in range(0,len(active_data)):
    #s=active_data[n]
    s=case_data[n]
    if s.name in fit_regions:
        # Generate look-ahead data based on exponenetial best fit
        #idx=np.argwhere(s.y > 50.0)
        idx=np.argwhere(s.t >= t0_1)
        t_fit=s.t[idx[0][0]:]-tmin_ts
        y_fit=np.log(s.y[idx[0][0]:])
        curve_fit=np.polyfit(t_fit,y_fit,1,w=np.sqrt(y_fit))
        t_fit=np.arange(t0_1,tmax_ts,86400.0)-tmin_ts # Generate t axis with look-ahead 10 days
        y_fit = np.exp(curve_fit[1]) * np.exp(curve_fit[0]*t_fit)
        #print(t_fit,y_fit)
        t=[]
        for tval in t_fit:
            t.append(dt.datetime.fromtimestamp(int(tval+tmin_ts)))
            if tval>tmax: tmax=tval
        #fit_ln,=ax1.semilogy(t,y_fit,':',color=plot_colours[s.name])
        #fit_lines.append(fit_ln)
        fit2_data[s.name]=[t,y_fit]

c.close()
##########################################################################################
#fig1, ax = plt.subplots(2,1)
fig1, ax1 = plt.subplots(figsize=(12, 6), dpi=150)
#fig2, ax2 = plt.subplots(figsize=(12, 6), dpi=150)
lines=[]
fit_lines=[]
n=0
ymax=0

n=0
tlims=[dt.datetime(2020,3,9),dt.datetime.fromtimestamp(int(tmax+tmin_ts))]
for n in range(0,len(active_data)):
    #s=active_data[n]
    s=case_data[n]
    drate=100.0*(death_data[n].y[-1]/case_data[n].y[-1])
    max_cases=np.nanmax(s.y)
    t=[]
    for tval in s.t:
        t.append(dt.datetime.fromtimestamp(int(tval)))
    ln,=ax1.semilogy(t,s.y,'-',color=plot_colours[s.name])
    if wa_only:
        ln.set_label(f'Confirmed Cases')
    else:
        ln.set_label(s.name)
    lines.append(ln)
    if s.name in fit_data.keys():
        """
        # Generate look-ahead data based on exponenetial best fit
        idx=np.argwhere(s.y > 10.0)
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
        """
        if wa_only:
            color1='royalblue'
            color2='green'
            color3='red'
            line_stylea='-'
            line_styleb='-'
        else:
            color1=plot_colours[s.name]
            color2=plot_colours[s.name]
            color3=plot_colours[s.name]
            line_stylea='+'
            line_styleb='*'
        lna,=ax1.semilogy(fit_data[s.name][0],fit_data[s.name][1],line_stylea,color=color1,alpha=0.5)
        lnb,=ax1.semilogy(fit2_data[s.name][0],fit2_data[s.name][1],line_styleb,color=color2,alpha=0.5)
        if wa_only:
            lna.set_label(f"Best fit using data since {dt.datetime.fromtimestamp(t0_0).strftime('%d-%b')}")
            lines.append(lna)
        if wa_only:
            lnb.set_label(f"Best fit using data since {dt.datetime.fromtimestamp(t0_1).strftime('%d-%b')}")
            lines.append(lnb)
    ln,=ax1.semilogy(tlims,[max_active_cases[s.name],max_active_cases[s.name]],'-',color=color3,alpha=0.5)
    ln.set_label(f"Limit of ICU beds (assuming 5% severe rate)")
    lines.append(ln)
#tmax=35
ymax=100000
setup_taxis(ax1,"Date",tlims,[5,1],color='black')
setup_logyaxis(ax1,"Cases",[10,ymax],[ymax/10,ymax/20],color='black')
ax1.legend(lines, [l.get_label() for l in lines])
now=dt.datetime.now()
last_ts=dt.datetime.fromtimestamp(int(s.t[-1]))
ax1.set_title(f"""Western Australia COVID-19 Cases as of {last_ts.strftime('%d-%b')} (plot by @gergamel)
Case Data: https://github.com/CSSEGISandData/COVID-19, https://covid19data.com.au
ICU Bed Data: 2018 ANZICS CORE Report https://www.anzics.com.au/annual-reports""")
#ax1.title.set_url = 'https://github.com/CSSEGISandData/COVID-19'
#'https://data.oecd.org/healtheqt/hospital-beds.htm'
plt.show()

"""
lines=[]
n=0
for n in range(0,len(active_data)):
    #s=active_data[n]
    s=case_data[n]
    if s.name not in icu_beds.keys():continue
    t=[]
    for tval in s.t:
        t.append(dt.datetime.fromtimestamp(int(tval)))
    ln,=ax2.plot(t,100.0*0.05*s.y/icu_beds[s.name],'-',color=plot_colours[s.name])
    ln.set_label(f'{s.name}')
    lines.append(ln)
    if s.name in fit_data.keys():
        ln,=ax2.plot(fit_data[s.name][0],100.0*0.05*fit_data[s.name][1]/icu_beds[s.name],':',color=plot_colours[s.name])
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
setup_taxis(ax2,"Date",tlims,[5,1],color='black')
setup_yaxis(ax2,r"5% of Active Cases/ICU Beds(%)",[0,120],[20,1],color='black')
ax2.legend(lines, [l.get_label() for l in lines])
ax2.set_title(f"Estimated Severe Active Cases (based on 5% rate) on ICU Beds\nSRC: 2018 ANZICS CORE Report https://www.anzics.com.au/annual-reports/")
plt.show()
"""
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
