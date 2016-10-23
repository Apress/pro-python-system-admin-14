#!/usr/bin/env python

import sys
import urllib2, urllib
import time
import requests
from BeautifulSoup import BeautifulSoup
from optparse import OptionParser

NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
WEBSITE_LOGON  = 'https://auth.telegraph.co.uk/sam-ui/login.htm'
WEBSITE_LOGOFF = 'https://auth.telegraph.co.uk/sam-ui/logoff.htm'
WEBSITE_USER = 'user@example.com'
WEBSITE_PASS = 'password'

def test_logon_logoff():
    session = requests.Session()
    form_data = {'email': WEBSITE_USER, 'password': WEBSITE_PASS}
    status = []
    try:
        # test logon
        result = session.post(WEBSITE_LOGON, data=form_data)
        html_logon = result.text
        soup_logon = BeautifulSoup(html_logon)
        logon_ok = validate_logon(soup_logon.head.title.text, result.url)
        # test logoff
        result = session.get(WEBSITE_LOGOFF)
        html_logoff = result.text
        soup_logoff = BeautifulSoup(html_logoff)
        logoff_ok = validate_logoff(soup_logoff.head.title.text, result.url)

        if logon_ok and logoff_ok:
            status = [NAGIOS_OK, 'Logon/logoff operation']
        else:
            status = [NAGIOS_CRITICAL, 'ERROR: Failed to logon and then logoff to the web site']
    except:
        status = [NAGIOS_CRITICAL, 'ERROR: Failure in the logon/logoff test']
        import traceback
        traceback.print_exc()
    return status

def validate_logon(title, redirect_url):
    result = True
    if title.find('My Account') == -1:
        result = False
    if redirect_url != 'https://auth.telegraph.co.uk/customer-portal/myaccount/index.html':
        result = False
    return result

def validate_logoff(title, redirect_url):
    result = True
    if title.find('My Account') != -1:
        result = False
    if redirect_url != 'http://www.telegraph.co.uk':
        result = False
    return result

def main():
    parser = OptionParser()
    parser.add_option('-w', dest='time_warn', default=3.8, help="Warning threshold in seconds, defaul: %default")
    parser.add_option('-c', dest='time_crit', default=5.8, help="Critical threshold in seconds, default: %default")
    (options, args) = parser.parse_args()
    if float(options.time_crit) < float(options.time_warn):
        options.time_warn = options.time_crit
    start = time.time()
    code, message = test_logon_logoff()
    elapsed = time.time() - start
    if code != 0:
        print message
        sys.exit(code)
    else:
        if elapsed < float(options.time_warn):
            print "OK: Performed %s sucessfully in %f seconds" % (message, elapsed)
            sys.exit(NAGIOS_OK)
        elif elapsed < float(options.time_crit):
            print "WARNING: Performed %s sucessfully in %f seconds" % (message, elapsed)
            sys.exit(NAGIOS_WARNING)
        else:
            print "CRITICAL: Performed %s sucessfully in %f seconds" % (message, elapsed)
            sys.exit(NAGIOS_CRITICAL)


if __name__ == '__main__':
    main()
