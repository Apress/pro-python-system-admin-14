#!/usr/bin/env python

import multiprocessing
import time
from datetime import datetime

class Oscillator(multiprocessing.Process):

    def __init__(self, event, period):
        self.period = period
        self.event = event
        super(Oscillator, self).__init__()

    def run(self):
        try:
            while True:
                self.event.clear()
                time.sleep(self.period)
                self.event.set()
        except KeyboardInterrupt:
            pass

class Scheduler(multiprocessing.Process):

    def __init__(self, event):
        self.event = event
        super(Scheduler, self).__init__()

    def run(self):
        try:
            while True:
                self.event.wait()
                print datetime.now()
        except KeyboardInterrupt:
            pass

mgr = multiprocessing.Manager()
e = mgr.Event()
o = Oscillator(e, 60)
s = Scheduler(e)
o.start()
s.start()
try:
    while len(multiprocessing.active_children()) != 0:
        time.sleep(1)
except KeyboardInterrupt:
    o.terminate()
    s.terminate()
o.join()
s.join()
