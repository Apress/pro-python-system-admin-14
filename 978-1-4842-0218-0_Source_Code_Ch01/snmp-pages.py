#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
from ConfigParser import SafeConfigParser
import rrdtool
import sys

WEBSITE_ROOT = '/home/rytis/public_html/snmp-monitor/'

def generate_index(systems, env, website_root):
    template = env.get_template('index.tpl')
    f = open("%s/index.html" % website_root, 'w')
    f.write(template.render({'systems': systems}))
    f.close()

def generate_details(system, env, website_root):
    template = env.get_template('details.tpl')
    for check_name, check_obj in system['checks'].iteritems():
        rrdtool.graph ("%s/%s.png" % (website_root, check_name),
                      '--title', "%s" % check_obj['description'],
                      "DEF:data=%(name)s.rrd:%(name)s:AVERAGE" % {'name': check_name},
                      'AREA:data#0c0c0c')
        f = open("%s/%s.html" % (website_root, str(check_name)), 'w')
        f.write(template.render({'check': check_obj, 'name': check_name}))
        f.close()

def generate_website(conf_file="", website_root=WEBSITE_ROOT):
    if not conf_file:
        sys.exit(-1)
    config = SafeConfigParser()
    config.read(conf_file)
    loader = FileSystemLoader('.')
    env = Environment(loader=loader)
    systems = {}
    for system in [s for s in config.sections() if s.startswith('system')]:
        systems[system] = {'description': config.get(system, 'description'),
                           'address'    : config.get(system, 'address'),
                           'port'       : config.get(system, 'port'),
                           'checks'     : {}
                          }
    for check in [c for c in config.sections() if c.startswith('check')]:
        systems[config.get(check, 'system')]['checks'][check] = {
                                                'oid'        : config.get(check, 'oid'),
                                                'description': config.get(check, 'description'),
                                                                }
    
    generate_index(systems, env, website_root)
    for system in systems.values():
        generate_details(system, env, website_root)


if __name__ == '__main__':
    generate_website(conf_file='snmp-manager.cfg')
