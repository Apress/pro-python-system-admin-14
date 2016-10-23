#!/usr/bin/env python

import cherrypy
import sqlite3
import socket
from cherrypy import _cptools
from MonitorLib import *
from ConfigParser import SafeConfigParser

class Root(_cptools.XMLRPCController):

    def __init__(self, cm):
        self.cm = cm

    @cherrypy.expose
    def cmd_store_probe_data(self, ticket, probe, tstamp):
        # probe - [ret_code, data_string]
        self.store_reading(ticket, probe, tstamp)
        return 'OK'

    @cherrypy.expose
    def cmd_get_new_monitor_url(self, host):
        port = cherrypy.config.get('server.socket_port') if cherrypy.config.get('server.socket_port') else 8080
        host = cherrypy.config.get('server.socket_host') if cherrypy.config.get('server.socket_host') else '127.0.0.1'
        server_url = "http://%s:%s/xmlrpc/" % (host, str(port))
        con = sqlite3.connect('monitor.db')
        res = con.execute("""SELECT hostparams.value 
                                           FROM hostparams, host, systemparams
                                          WHERE host.id = hostparams.host_id
                                            AND systemparams.name = 'monitor_url'
                                            AND hostparams.param_id = systemparams.id
                                            AND host.address = ?""", (host,) ).fetchone()
        if not res:
            res = con.execute("SELECT value FROM systemparams WHERE name = 'monitor_url'").fetchone()
        if res:
            server_url = res[0]
        return server_url

    @cherrypy.expose
    def cmd_get_sensor_code(self, sensor):
        with open("%s/%s.tar.bz2" % (self.cm.sensor.source_dir, sensor), 'rb') as f:
            return xmlrpclib.Binary(f.read())


    @cherrypy.expose
    def healthcheck(self):
        return 'OK'


    def store_reading(ticket, probe, tstamp):
        con = sqlite3.connect('monitor.db')
        res = [r[0] for r in con.execute('SELECT hostprobe_id FROM ticketqueue WHERE id=?', (ticket,) )][0]
        if res:
            con.execute('DELETE FROM ticketqueue WHERE id=?', (ticket,) )
            con.execute('INSERT INTO probereading VALUES (NULL, ?, ?, ?, ?)', (res, str(tstamp), float(probe[1].strip()), int(probe[0])))
            con.commit()
        else:
            print 'Ticket does not exist: %s' % str(ticket)

class ConfigManager(object):

    class Section:
        def __init__(self, name, parser):
            self.__dict__['name'] = name
            self.__dict__['parser'] = parser
            #reason for using __dict__ is that __setattr__ is called to initiate all local class attrs and so
            #declaring the below would cause __setattr__ to be called and obviously neither name nor parser exist yet
            #self.name = name
            #self.parser = parser

        def __setattr__(self, option, value):
            self.__dict__[option] = str(value)
            self.parser.set(self.name, option, str(value))

    def __init__(self, file_name):
        self.parser = SafeConfigParser()
        self.parser.read(file_name)
        self.file_name = file_name
        for section in self.parser.sections():
            setattr(self, section, self.Section(section, self.parser))
            for option in self.parser.options(section):
                setattr(getattr(self, section), option, self.parser.get(section, option))

    def __getattr__(self, option):
        self.parser.add_section(option)
        setattr(self, option, Section(option, self.parser))
        return getattr(self, option)

    def save_config(self):
        f = open(self.file_name, 'w')
        self.parser.write(f)
        f.close()



if __name__ == '__main__':
    cm = ConfigManager('server.cfg')
    cherrypy.config.update({'server.socket_port': 8081})
    cherrypy.config.update({'server.socket_host': socket.gethostname()})
    cherrypy.quickstart(Root(cm), '/xmlrpc')

