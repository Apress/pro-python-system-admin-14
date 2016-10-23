#!/usr/bin/env python

from datetime import datetime
import sqlite3
import numpy as np
#import matplotlib.pyplot as plt

###################
### Laptop CPU data

# periodic amplification (laptop)
# 0 -> 1
pl = np.sin(2*np.pi*np.arange(100800)/1440)
pl[pl<0] = np.random.rand(1440/2)*0.1
# data (laptop)
# 0 -> ~3
cl = np.random.pareto(10, size=100800) * 2
# result
cpu_l = cl * pl

###################
### Server CPU data

# periodic amplification (server)
# 0 -> 1
ps = np.sin(2*np.pi*np.arange(100800)/1440)
ps[ps<0.5] = np.sin(2*np.pi*np.arange(50, 1440/2 - 50)/(1440))*0.3 + 0.3
# data (server)
# ~1 -> ~7
cs = np.random.normal(4, 0.9, 100800)
cs[cs<0] = 0
# trend function
tp = np.sin(2*np.pi*np.arange(100800)/(1440*7))*0.1+0.1
tl = np.arange(100800.)/(100800./1.)
tf = tp + tl + 1
# result
cpu_s = cs * ps * tf

########################
### Server HTTP req data

# periodic amplification (server)
# 0 -> 1
psh = np.sin(2*np.pi*np.arange(100800)/1440)
psh[psh>0.7] = 0.9/np.linspace(1., 2.2, 100800)
psh[psh<0.5] = np.sin(2*np.pi*np.arange(50, 1440/2 - 50)/(1440))*0.3 + 0.3
# data (server)
# ~1 -> ~7
csh = np.random.normal(400, 100, 100800)
csh[csh<0] = 0
# trend function
tph = np.sin(2*np.pi*np.arange(100800)/(1440*7))*0.1+0.1
tlh = np.arange(100800.)/(100800./1.)
tfh = tph + tlh + 1
# result
http_s = csh * psh * tfh * 0.7 + 200

con = sqlite3.connect('monitor.db')

# datetime.fromtimestamp(1260999020).isoformat()

# cpu_l
# hostprobe_id = 1

for i in range(len(cpu_l)):
    con.execute("INSERT INTO probereading (hostprobe_id, timestamp, probe_value, ret_code) VALUES (?, ?, ?, ?);", 
                (1, datetime.fromtimestamp(1260999020+i*60).isoformat(), cpu_l[i], 0)
               )
con.commit()

# cpu_s
# hostprobe_id = 2

for i in range(len(cpu_s)):
    con.execute("INSERT INTO probereading (hostprobe_id, timestamp, probe_value, ret_code) VALUES (?, ?, ?, ?);", 
                (2, datetime.fromtimestamp(1260999020+i*60).isoformat(), cpu_s[i], 0)
               )
con.commit()
# http_s
# hostprobe_id = 3

for i in range(0, len(http_s), 5):
    con.execute("INSERT INTO probereading (hostprobe_id, timestamp, probe_value, ret_code) VALUES (?, ?, ?, ?);", 
                (3, datetime.fromtimestamp(1260999020+i*60).isoformat(), http_s[i], 0)
               )
con.commit()

#plt.plot(http_s)
#plt.show()
