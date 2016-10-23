#!/usr/bin/env python

import re
import sys
import urllib2
import urlparse
import time
from BeautifulSoup import BeautifulSoup
from optparse import OptionParser
import traceback

NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
WEBSITE_ROOT = 'http://www.bbc.co.uk/news/'

def fetch_top_story():
    status = []
    try:
        result = urllib2.urlopen(WEBSITE_ROOT)
        html = result.read()
        soup = BeautifulSoup(html)
        # apparently there are two types of 'top stories' at BBC
        # one that spans across two columns with a large picture. this one is 'tshsplash'
        # another with the picture sharing the same space. this is called 'tsh'
        # either case the <a> tag of class that starts with "tsh" is unique
        # i suspect the 'tsh' means TopStoryHeading or something similar.
        # the book text assumes 'tshsplash' scenario only!
        # this code however handles both cases correctly
        top_story_div = soup.find('div', {'id': 'top-story'})
        h2_tag = top_story_div.find('h2', {'class': 'top-story-header '})
        a_tag = h2_tag.find('a', {'class': 'story'})
        story_heading = a_tag.text
        topstory_url = ''
        if a_tag.has_key('href'):
            topstory_url = urlparse.urljoin(WEBSITE_ROOT, a_tag['href'])
        else:
            status = [NAGIOS_CRITICAL, 'ERROR: Top story anchor tag has no link']
        result = urllib2.urlopen(topstory_url)
        html = result.read()
        status = [NAGIOS_OK, story_heading]
    except:
        traceback.print_exc()
        status = [NAGIOS_CRITICAL, 'ERROR: Failed to retrieve the top story']
    return status


def main():
    parser = OptionParser()
    parser.add_option('-w', dest='time_warn', default=1.8, help="Warning threshold in seconds, defaul: %default")
    parser.add_option('-c', dest='time_crit', default=3.8, help="Critical threshold in seconds, default: %default")
    (options, args) = parser.parse_args()
    if float(options.time_crit) < float(options.time_warn):
        options.time_warn = options.time_crit
    start = time.time()
    code, message = fetch_top_story()
    elapsed = time.time() - start
    if code != 0:
        print message
        sys.exit(code)
    else:
        if elapsed < float(options.time_warn):
            print "OK: Top story '%s' retrieved in %f seconds" % (message, elapsed)
            sys.exit(NAGIOS_OK)
        elif elapsed < float(options.time_crit):
            print "WARNING: Top story '%s' retrieved in %f seconds" % (message, elapsed)
            sys.exit(NAGIOS_WARNING)
        else:
            print "CRITICAL: Top story '%s' retrieved in %f seconds" % (message, elapsed)
            sys.exit(NAGIOS_CRITICAL)


if __name__ == '__main__':
    main()
