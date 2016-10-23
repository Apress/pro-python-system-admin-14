#!/usr/bin/env python

import re
import os, sys
from ConfigParser import SafeConfigParser
import MySQLdb
from plugin_manager import PluginManager


def main():
    cfg = SafeConfigParser()
    cfg.read('mysql_db.cfg')
    plugin_manager = PluginManager()
    connection = MySQLdb.connect(user=cfg.get('main', 'user'),
                                 passwd=cfg.get('main', 'passwd'),
                                 host=cfg.get('main', 'host'))
    env_vars = plugin_manager.call_method('generate', keywords=['provider'], args={'connection': connection})
    plugin_manager.call_method('process', keywords=['consumer'], args={'connection': connection, 'env_vars': env_vars})
    plugin_manager.call_method('report')

if __name__ == '__main__':
    main()
