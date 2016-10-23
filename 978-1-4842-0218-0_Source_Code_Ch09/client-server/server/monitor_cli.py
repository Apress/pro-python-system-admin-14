#!/usr/bin/env python

from MonitorLib import *
from optparse import OptionParser
import sys

OPTIONS = {}
ARGS = []


def parse_options(cfg):
    global OPTIONS, ARGS

    usage = """Usage: %prog command [options]"""
    p = OptionParser(usage)
    p.add_option('-a', '--address', dest='address', default=None, metavar='ADDRESS', 
                 help='Connect to the client at ADDRESS')
    p.add_option('-p', '--port', dest='port', default='8080', metavar='PORT',
                 help='Specify port number [default: %default]')
    p.add_option('-s', '--sensor', dest='sensor', default=None, metavar='SENSOR',
                 help='Request readings from sensor named SENSOR')
    p.add_option('-o', '--options', dest='options', default=None, metavar='STRING',
                 help='Pass STRING as a comma separated list to the sensor')
    p.add_option('-h', '--hostprobe', dest='hostprobe', default=None, metavar='HOSTPROBEID',
                 help='Run specific hostprobe check, all options ignored and data from DB is used')

    (OPTIONS, ARGS) = p.parse_args()
    
    # do we have incorrect number of arguments?
    if len(ARGS) != 1:
        p.print_help()
        sys.exit(-1)
    # is this a valid command?
    if ARGS[0] not in cfg.COMMANDS:
        print "ERROR: Unknown command '%s'" % ARGS[0]
        print 'Valid commands are:'
        for c in cfg.COMMANDS:
            print c
        p.print_help()
        sys.exit(-1)
    # do we have all required vars for the command?
    for var in cfg.COMMANDS[ARGS[0]]:
        if not getattr(OPTIONS, var):
            print "ERROR: Missing required option: '%s'" % var
            p.print_help()
            sys.exit(-1)

class CommandLineReport():
    def __init__(self):
        pass

    def read(self, result):
        print result

    def list_sensors(self, sensor_list):
        print 'The following sensors are available:'
        for sensor_name, options in sensor_list.iteritems():
            print '- %s' % sensor_name
            for opt in options.strip().split("\n"):
                print '    %s' % opt


if __name__ == '__main__':
    cfg = MonitorConfig()
    parse_options(cfg)
    mc = MonitorClient(OPTIONS.address, OPTIONS.port)
    if OPTIONS.sensor:
        opt_list = [o for o in OPTIONS.options.split(',')] if OPTIONS.options else None
        mc.set_sensor(OPTIONS.sensor, opt_list)
    res = getattr(mc, "execute_%s" % ARGS[0])()
    clr = CommandLineReport()
    getattr(clr, ARGS[0])(res)
