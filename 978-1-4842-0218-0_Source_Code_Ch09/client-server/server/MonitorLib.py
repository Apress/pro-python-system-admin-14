#!/usr/bin/env python

import xmlrpclib
import sqlite3

class MonitorConfig():
    def __init__(self):
        self.COMMANDS = { 'read':          ['address', 'sensor'], 
                          'set_server':    ['address'], 
                          'update_sensor': ['address', 'sensor'],
                          'list_sensors':  ['address'],
                        }

class MonitorClient():

    def __init__(self, address, port='8080'):
        self.url = "http://%(address)s:%(port)s/xmlrpc/" % {'address': address, 'port': port}
        self.sensor = None
        self.sensor_opts = None
        self.proxy = self.get_xmlrpc_proxy()

    def set_sensor(self, name, options=None):
        self.sensor = name
        self.sensor_opts = options

    def get_xmlrpc_proxy(self):
        proxy = xmlrpclib.ServerProxy(self.url, allow_none=True)
        return proxy

    # All 'command' functions must have the following naming convention: 'execute_<command name>'
    def execute_read(self, hostprobe=None):
        # the code below tries to find hostprobe id by matching supplied
        # hostname, probe and options strings against the configuration DB
        # if found, it will then raise a request ticket and submit it to the client
        
        #if not hostprobe:
        #    con = sqlite3.connect('monitor.db')
        #    res = con.execute('SELECT * from

        # the following is for unconditional execution (used for testing only)
        return self.proxy.cmd_submit_reading(self.sensor, self.sensor_opts)

    def execute_list_sensors(self):
        return self.proxy.cmd_list_sensors()





if __name__ == '__main__':
    pass
