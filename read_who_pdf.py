import PyPDF2
import re

row_re=re.compile(r"(\|\D+\|\s+\|\d+\|\s+\|\d+\|\s+\|\d+\|\s+\|\d+\|\s+\|\D+\|\s+\|\d+)")
subrow_re=re.compile(r"\|(\D+)\|\s+\|(\d+)\|\s+\|(\d+)\|\s+\|(\d+)\|\s+\|(\d+)\|\s+\|(\D+)\|\s+\|(\d+)")

def parse_match(m):
    d={}
    x=m.groups()
    loc=x[0].split('|')
    if loc[-1]=='':
        d['location']=loc[-2]
    else:
        d['location']=loc[-1]
    d['cases']=x[1]
    d['new_cases']=x[2]
    d['deaths']=x[3]
    d['new_deaths']=x[4]
    d['days_since']=x[6]
    #print(f"{location},{cases},{new_cases},{deaths},{new_deaths},{days_since}")
    return d

f=open('20200318-sitrep-58-covid-19.pdf','rb')
reader=PyPDF2.PdfFileReader(f)
num_pages=reader.numPages
n=0
while n<num_pages:
    page=reader.getPage(n)
    text=page.extractText().replace('\n','|')
    if "Reporting Country" in page.extractText():
        break
    n+=1

data=[]
while n<num_pages:
    page=reader.getPage(n)
    text=page.extractText().replace('\n','|')
    for trow in row_re.split(text):
        m = subrow_re.match(trow)
        if m is None: continue
        data.append(parse_match(m))
    n+=1

f.close()

for d in data:
    print(d)
