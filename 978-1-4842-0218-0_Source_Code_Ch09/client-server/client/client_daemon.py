#!/usr/bin/env python

import cherrypy
import subprocess
import os, sys
import shutil
import xmlrpclib
import socket
import tempfile
import tarfile
from cherrypy import _cptools
from datetime import datetime
from ConfigParser import SafeConfigParser


class Root(_cptools.XMLRPCController):
    def __init__(self, conf_manager):
        self.cm = conf_manager

    @cherrypy.expose
    def cmd_submit_reading(self, ticket, sensor_name, arguments=None):
        cmd = ['%s/%s/%s' % (cm.sensor.path, sensor_name, cm.sensor.executable)]
        if arguments:
            cmd.extend([str(a) for a in arguments])
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        resp_msg = p.communicate()[0]
        ret_code = p.returncode 
        self.submit_reading(ticket, ret_code, resp_msg)
        return (ret_code, resp_msg)

    @cherrypy.expose
    def cmd_list_sensors(self):
        sensors = [d for d in os.listdir(self.cm.sensor.path) if 
                              os.path.isdir('%s/%s' % (self.cm.sensor.path, d)) and 
                              os.path.exists('%s/%s/%s' % (self.cm.sensor.path, d, self.cm.sensor.executable))]
        result = {}
        for s in sensors:
            cmd = '%(dir)s/%(sensor)s/%(exec)s %(opt)s' % { 'dir':    self.cm.sensor.path,
                                                            'sensor': s,
                                                            'exec':   self.cm.sensor.executable,
                                                            'opt':    self.cm.sensor.help }
            p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
            result[s] = p.communicate()[0]
        return result

    @cherrypy.expose
    def cmd_register_new_server(self):
        hostname = socket.gethostname()
        proxy = xmlrpclib.ServerProxy(self.cm.monitor.url)
        url = proxy.cmd_get_new_monitor_url(hostname)
        try:
            proxy = xmlrpclib.ServerProxy(url)
            res = proxy.healthcheck()
            if res == 'OK':
                self.cm.monitor.url = url
                self.cm.save_config()
        except:
            pass
        return 'OK'

    @cherrypy.expose
    def cmd_update_sensor_code(self, sensor):
        # get the new file
        proxy = xmlrpclib.ServerProxy(self.cm.monitor.url)
        tmp_dir = tempfile.mkdtemp(dir='.')
        dst_file = "%s/%s.tar.bz2" % (tmp_dir, sensor)
        with open(dst_file, 'wb') as f:
            f.write(proxy.cmd_get_sensor_code(sensor).data)
            f.close()
        # unpack it
        arch = tarfile.open(dst_file)
        arch.extractall(path=tmp_dir)
        arch.close()
        # check it
        cmd = ["%s/%s/%s" % (tmp_dir, sensor, self.cm.sensor.executable), "options"]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        p.communicate()
        if p.returncode != 0:
            # remove if fails
            shutil.rmtree(tmp_dir)
        else:
            # backup the existing package
            sens_dir = "%s/%s" % (self.cm.sensor.path, sensor)
            bck_dir = "%s/%s_%s" % (self.cm.sensor.backup, sensor, datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%S'))
            try:
                shutil.move(sens_dir, bck_dir)
            except:
                pass
            os.remove(dst_file)
            # replace with new
            shutil.move("%s/%s" % (tmp_dir, sensor), sens_dir)
            os.rmdir(tmp_dir)
        return 'OK'

    def submit_reading(self, ticket, ret_code, resp_msg):
        proxy = xmlrpclib.ServerProxy(self.cm.monitor.url)
        tstamp = datetime.now()
        res = proxy.cmd_store_probe_data(ticket, [ret_code, resp_msg], tstamp)
        return


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

    def __getattr__(self, section):
        self.parser.add_section(section)
        setattr(self, section, Section(section, self.parser))
        return getattr(self, section)

    def save_config(self):
        f = open(self.file_name, 'w')
        self.parser.write(f)
        f.close()



if __name__ == '__main__':
    cm = ConfigManager('client.cfg')
    cherrypy.quickstart(Root(cm), '/xmlrpc')
