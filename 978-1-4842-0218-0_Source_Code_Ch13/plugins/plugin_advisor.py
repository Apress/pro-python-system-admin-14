
from plugin_manager import Plugin
import urllib2
from BeautifulSoup import BeautifulSoup

class PerformanceAdvisor(Plugin):

    def __init__(self, **kwargs):
        self.keywords = ['consumer']
        print self.__class__.__name__, 'initialising...'

    def process(self, **kwargs):
        print self.__class__.__name__, 'processing data...'

    def report(self, **kwargs):
        print self.__class__.__name__, 'reporting...'


class KeyBufferSizeAdvisor(Plugin):

    def __init__(self, **kwargs):
        self.keywords = ['consumer']
        self.physical_mem = 0
        self.key_buffer = 0
        self.ratio = 0.0
        self.recommended_buffer = 0
        self.recommended_ratio = 0.4

    def process(self, **kwargs):
        self.key_buffer = int(kwargs['env_vars']['ServerSystemVariables']['key_buffer_size'])
        self.physical_mem = int(kwargs['env_vars']['HostProperties']['mem_phys_total'])
        self.ratio = float(self.key_buffer) / self.physical_mem
        self.recommended_buffer = int(self.physical_mem * self.recommended_ratio)

    def report(self, **kwargs):
        print self.__class__.__name__, 'reporting...'
        print "The key buffer size currently is %d" % self.key_buffer
        if self.ratio < self.recommended_ratio:
            print "This setting seems to be too small for the amount of memory installed: %d" % self.physical_mem
        else:
            print "You may have allocated too much memory for the key buffer"
            print "You currently have %d, you must free up some memory"
        print "Consider setting key_buffer_size to %d, if the difference is too high" % self.recommended_buffer


class SlowQueriesAdvisor(Plugin):

    def __init__(self, **kwargs):
        self.keywords = ['consumer']
        self.log_slow = False
        self.long_query_time = 0
        self.total_slow_queries = 0
        self.total_requests = 0
        self.long_qry_ratio = 0.0 # in %
        self.threshold = 0.0001   # in %
        self.advise = ''

    def process(self, **kwargs):
        if kwargs['env_vars']['ServerSystemVariables']['log_slow_queries'] == 'ON':
            self.log_slow = True
        self.long_query_time = float(kwargs['env_vars']['ServerSystemVariables']['long_query_time'])
        self.total_slow_queries = int(kwargs['env_vars']['ServerStatusVariables']['Slow_queries'])
        self.total_requests = int(kwargs['env_vars']['ServerStatusVariables']['Questions'])
        self.long_qry_ratio = (100. * self.total_slow_queries) / self.total_requests

    def report(self, **kwargs):
        print self.__class__.__name__, 'reporting...'
        if self.log_slow:
            print "There are %d slow requests out of total %d, which is %f%%" % (self.total_slow_queries,
                                                                                 self.total_requests,
                                                                                 self.long_qry_ratio)
            print "Currently all queries taking longer than %f are considered slow" % self.long_query_time
            if self.long_qry_ratio < self.threshold:
                print 'The current slow queries ratio seems to be reasonable'
            else:
                print 'You seem to have lots of slow queries, investigate them and possibly increase long_query_time'
        else:
            print 'The slow queries are not logged, set log_slow_queries to ON for tracking'


class MySQLVersionAdvisor(Plugin):

    def __init__(self, **kwargs):
        self.keywords = ['consumer']
        self.advices = []
        self.installed_release = None
        self.latest_release = None

    def _check_latest_ga_release(self):
        html = urllib2.urlopen('http://www.mysql.com/downloads/mysql/')
        soup = BeautifulSoup(html)
        tags = soup.findAll('h1')
        version_str = tags[1].string.split()[-1]
        (major, minor, release) = [int(i) for i in version_str.split('.')]
        return (major, minor, release)
        

    def process(self, **kwargs):
        version = kwargs['env_vars']['ServerSystemVariables']['version'].split('-')[0]
        (major, minor, release) = [int(i) for i in version.split('.')]
        latest_major, latest_minor, latest_rel = self._check_latest_ga_release()
        self.installed_release = (major, minor, release)
        self.latest_release = (latest_major, latest_minor, latest_rel)
        if major < latest_major:
            self.advices.append(('CRITICAL', 'There is a newer major release available, you should upgrade'))
        elif major == latest_major and minor < latest_minor:
            self.advices.append(('WARNING', 'There is a newer minor release available, consider an upgrade'))
        elif major == latest_major and minor == latest_minor and release < latest_rel:
            self.advices.append(('NOTE', 'There is a newer update release available, consider a patch'))
        else:
            self.advices.append(('OK', 'Your installation is up to date'))
        
    def report(self, **kwargs):
        print self.__class__.__name__, 'reporting...'
        print "The running server version is: %d.%d.%d" % self.installed_release
        print "The latest available GA release is: %d.%d.%d" % self.latest_release
        for rec in self.advices:
            print "%10s: %s" % (rec[0], rec[1])
        
