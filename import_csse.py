#!/usr/bin/env python3
import covid
import datetime as dt

c=covid.Session()
c.flush()
c.import_data()
c.update_data()
c.close()