#!/usr/bin/env python

import sqlite3
import time
import sys
import multiprocessing
import xmlrpclib
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


class TicketScheduler(multiprocessing.Process):

    def __init__(self, event):
        self.event = event
        self.con = sqlite3.connect('monitor.db')
        super(TicketScheduler, self).__init__()

    def run(self):
        try:
            from datetime import datetime
            while True:
                self.event.wait()
                res = [r[0] for r in self.con.execute("""SELECT hostprobe_id 
                                                           FROM probingschedule 
                                                          WHERE (strftime('%s', 'now')/60) % probingschedule.probeinterval = 0;""")]
                for probe_id in res:
                    self.con.execute("INSERT INTO ticketqueue VALUES (NULL, ?, datetime('now'), 0)", (probe_id,))
                    self.con.commit()
        except KeyboardInterrupt:
            pass


class TicketDispatcher(multiprocessing.Process):

    def __init__(self, max_delay=10):
        self.delay = 1
        self.max_delay = max_delay
        self.con = sqlite3.connect('monitor.db')
        super(TicketDispatcher, self).__init__()

    def run(self):
        try:
            while True:
                time.sleep(self.delay)
                pending_tickets = [r for r in self.con.execute("SELECT id, hostprobe_id FROM ticketqueue WHERE dispatched = 0")]
                if not pending_tickets and self.delay < self.max_delay:
                    self.delay += 1
                elif self.delay > 1:
                    self.delay -= 1
                for (ticket_id, hostprobe_id) in pending_tickets:
                    res = [r for r in self.con.execute("""SELECT host.address, host.port, sensor.name, probe.parameter
                                                            FROM hostprobe, host, probe, sensor
                                                           WHERE hostprobe.id=?
                                                                 AND hostprobe.host_id = host.id
                                                                 AND hostprobe.probe_id = probe.id
                                                                 AND probe.sensor_id = sensor.id""", (hostprobe_id,) )][0]
                    self._send_request(ticket_id, res[0], res[1], res[2], res[3])
                    self.con.execute("UPDATE ticketqueue SET dispatched=1 WHERE id=?", (ticket_id,))
                    self.con.commit()
        except KeyboardInterrupt:
            pass

    def _send_request(self, ticket, address, port, sensor, parameter_string=None):
        url = "http://%s:%s/xmlrpc/" % (address, port)
        proxy = xmlrpclib.ServerProxy(url, allow_none=True)
        if parameter_string:
            parameter = parameter_string.split(',')
        else:
            parameter = None
        print ticket
        print sensor
        print parameter
        res = proxy.cmd_submit_reading(ticket, sensor, parameter)
        return


def start_processes():
    clock = multiprocessing.Event()
    o = Oscillator(clock, 60)
    s = TicketScheduler(clock)
    d = TicketDispatcher()
    o.start()
    s.start()
    d.start()
    try:
        while True:
            time.sleep(1)
            if len(multiprocessing.active_children()) == 0:
                break
    except KeyboardInterrupt:
        pass


def register_new_server(host, port):
    proxy = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/' % (host, str(port)))
    res = proxy.cmd_register_new_server()

def update_sensor_code(host, port, sensor):
    proxy = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/' % (host, str(port)))
    res = proxy.cmd_update_sensor_code(sensor)

if __name__ == '__main__':
    update_sensor_code('localhost', 8080, 'disk')
    sys.exit()
    start_processes()
