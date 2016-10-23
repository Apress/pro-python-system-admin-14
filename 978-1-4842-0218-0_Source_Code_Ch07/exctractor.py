#!/usr/bin/env python
##
## Exctractor - Java exception extractor v0.1
##
## Usage: exctractor.py [options] LOG_DIR1 [LOG_DIR2 [LOG_DIR3 [...]]]
## 
## options:
##       -h, --help                                show this help message and exit
##       -p FILE_PATTERN, --pattern=FILE_PATTERN   Pattern for log files
##       -f FORMAT, --format=FORMAT                Output format: CSV (default) or TEXT
##       -g                                        Include group statistics in the report (TEXT mode only; enables TEXT mode)
##       -v                                        Verbose output (TEXT mode only; enables TEXT mode)
##
## Description:
## - Parses all log files (tries to differentiate between plain text and bzip files)
## - Looks for text blocks that potentially can be exceptions:
##   . block starts with the timestamp
##   . is followed by 1 or more lines without a timestamp
## - Block is validated to be an exception:
##   . shall contain words 'exception' and 'java'
## - Block is then dissected into:
##   . log line (one with the timestamp)
##   . first exception line
##   . exception body
## - If the dissected exception matches one of the grouping rules (as defined in rules definition file) it is recorded
## - Otherwise it'll get identified by generating MD5 hash to it's body contents:
##   . Proxy objects removed
##   . '(...text...)' lines removed
##
## Format of the rules file:
##
## <?xml version="1.0"?>
## <config>
##    <exception_types>
##        <exception logline="<regexp to match the first log line (one that contains the timestamp)>" 
##                   headline="<regexp to match the first exception body line>"
##                   body="<regexp to match exception body>"
##                   group="<group name, any text>"
##                   desc="<group description, eny text>"
##        />
##    </exception_types>
## </config>
##
## Multiple rules can be grouped by using the same group name
##
## ---------------------------------------------------------------------------------------------------------------
## Exctractor - Java exception extractor
## Copyright (C) 2007 Rytis Sileika
## 
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
##

import bz2, sys, os, re, md5, random, operator
from xml.dom import minidom
from optparse import OptionParser

LOG_PATTERN = ".log"
BZLOG_PATTERN = ".log.bz2"
CONFIG_FILE = 'exctractor.xml'

TPL_SUMMARY = {}
TPL_SUMMARY['csv']  = "%(total)s, %(groups)s"
TPL_SUMMARY['text'] = "=" * 80 + "\nTotal exceptions: %(total)s\nDifferent groups: %(groups)s"

TS_RE_1 = re.compile("^\d\d\d\d.\d\d.\d\d")
#TS_RE_2 = re.compile("^\d\d.....\d\d\d\d")
#TS_RE_2 = re.compile("^... \d{2}, \d{4} \d{1-2}:\d{2}:\d{2}")
TS_RE_2 = re.compile("^... \d\d, \d\d\d\d")

OPTIONS = {}
DIRS = []

class ExceptionContainer:
    def __init__(self):
        self.exceptions = {}
        self.filters = []
        self.count = 0
        
        config = minidom.parse(CONFIG_FILE)
        
        for et in config.getElementsByTagName('exception_types'):
            for e in et.getElementsByTagName('exception'):
                m = md5.new()
                m.update(e.attributes['logline'].value)
                m.update(e.attributes['headline'].value)
                m.update(e.attributes['body'].value)
                self.filters.append({ 'id'   : m.hexdigest(),
                                      'll_re': re.compile(e.attributes['logline'].value),
                                      'hl_re': re.compile(e.attributes['headline'].value),
                                      'bl_re': re.compile(e.attributes['body'].value),
                                      'group': e.attributes['group'].value,
                                      'desc' : e.attributes['desc'].value, })
            
        
    def insert(self, suspect_body, f_name=""):
        lines = suspect_body.strip().split("\n", 1)
        log_l = lines[0]
        if self.is_exception(lines[1]):
            self.count += 1
            try:
                hd_l, bd_l = lines[1].strip().split("\n", 1)
            except:
                hd_l, bd_l = (lines[1].strip(), "")
            
            logged = False
            
            for f in self.filters:
                if f['ll_re'].search(log_l) and f['hl_re'].search(hd_l) and f['bl_re'].search(bd_l):
                    logged = True
                    if f['id'] in self.exceptions:
                        self.exceptions[f['id']]['count'] += 1
                    else:
                        self.exceptions[f['id']] = { 'count'    : 1,
                                                     'log_line' : log_l,
                                                     'header'   : hd_l,
                                                     'body'     : bd_l,
                                                     'f_name'   : f_name,
                                                     'desc'     : f['desc'],
                                                     'group'    : f['group'], }
                    break
            
            if not logged:
                m = md5.new()
                try:
                    m.update(log_l.split(" ", 3)[2])
                except:
                    pass
                m.update(hd_l)
                for ml in bd_l.strip().split("\n"):
                    if ml:
                        ml = re.sub("\(.*\)", "", ml)
                        ml = re.sub("\$Proxy", "", ml)
                        m.update(ml)
                if m.hexdigest() in self.exceptions:
                    self.exceptions[m.hexdigest()]['count'] += 1
                else:
                    self.exceptions[m.hexdigest()] = { 'count'    : 1,
                                                       'log_line' : log_l,
                                                       'header'   : hd_l,
                                                       'body'     : bd_l,
                                                       'f_name'   : f_name,
                                                       'desc'     : 'NOT IDENTIFIED',
                                                       'group'    : 'unrecognised_'+m.hexdigest(), }

    def is_exception(self, strace):
        if strace.lower().find('exception') != -1 and \
           strace.lower().find('java')      != -1:
            return True
        else:
            return False

    def print_status(self):
        categories = {}
        for e in self.exceptions:
            if self.exceptions[e]['group'] in categories:
                categories[self.exceptions[e]['group']] += self.exceptions[e]['count']
            else:
                categories[self.exceptions[e]['group']] = self.exceptions[e]['count']
            if OPTIONS.verbose:
                print '-' * 80
                print "Filter ID                 :", e
                print "Exception description     :", self.exceptions[e]['desc']
                print "Exception group           :", self.exceptions[e]['group']
                print "Exception count           :", self.exceptions[e]['count']
                print "First file                :", self.exceptions[e]['f_name']
                print "First occurrence log line :", self.exceptions[e]['log_line']
                print "Stack trace headline      :", self.exceptions[e]['header']
                print "Stack trace               :"
                print self.exceptions[e]['body']
        
        if OPTIONS.verbose:
            print '=' * 80

        print TPL_SUMMARY[OPTIONS.format.lower()] % {'total': self.count, 'groups': len(categories)}

        if OPTIONS.groups:
            print '=' * 80
            for i in sorted(categories.iteritems(), key=operator.itemgetter(1), reverse=True):
                print "%8s (%6.2f%%) : %s" % (i[1], 100 * float(i[1]) / float(self.count), i[0] )
            print '* Match first column (group name) with "Exception group" field in detailed list to get the exception details'


def get_suspect(g):
    line = g.next()
    next_line = g.next()
    while 1:
        if not (TS_RE_1.search(next_line) or TS_RE_2.search(next_line)):
            suspect_body = line
            while not (TS_RE_1.search(next_line) or TS_RE_2.search(next_line)):
                suspect_body += next_line
                next_line = g.next()
            yield suspect_body
        else:
            try:
                line, next_line = next_line, g.next()
            except:
                raise StopIteration

def parse_options():
    global OPTIONS, DIRS
    cli_parser = OptionParser("Usage: %prog [options] LOG_DIR1 [LOG_DIR2 [LOG_DIR3 [...]]]")
    cli_parser.add_option("-p", "--pattern", dest="file_pattern", help="Pattern for log files", default="")
    cli_parser.add_option("-f", "--format", dest="format", help="Output format: CSV (default) or TEXT", default="csv")
    cli_parser.add_option("-g", action="store_true", dest="groups", default=False, help="Include group statistics in the report (TEXT mode only; enables TEXT mode)")
    cli_parser.add_option("-v", action="store_true", dest="verbose", default=False, help="Verbose output (TEXT mode only; enables TEXT mode)")

    (OPTIONS, ARGS) = cli_parser.parse_args()
    if OPTIONS.groups or OPTIONS.verbose: OPTIONS.format = 'text'
    if OPTIONS.verbose: OPTIONS.groups = True

    if not ARGS:
        cli_parser.print_help()
        sys.exit(1)
    else:
        for dir in ARGS:
            for root, dirs, files in os.walk(dir):
                DIRS.append(root)

def main():
    ec = ExceptionContainer()
    parse_options()

    for DIR in DIRS:
        for file in (DIR + "/" + f for f in os.listdir(DIR) if f.find(LOG_PATTERN) != -1 and f.find(OPTIONS.file_pattern) != -1 ):
            try:
                if file.find(BZLOG_PATTERN) != -1:
                    fd = bz2.BZ2File(file, 'r')
                else:
                    fd = open(file, 'r')
                g = (line for line in fd)
                suspects = get_suspect(g)
                for suspect_body in suspects:
                    ec.insert(suspect_body, f_name=file)
            except:
                pass
    
    ec.print_status()

if __name__ == '__main__':
    main()
