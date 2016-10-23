
from plugin_manager import Plugin
import psutil


class ServerStatusVariables(Plugin):

    def __init__(self, **kwargs):
        self.keywords = ['provider']
        print self.__class__.__name__, 'initialising...'

    def generate(self, **kwargs):
        cursor = kwargs['connection'].cursor()
        cursor.execute('SHOW /*!50002 GLOBAL */ STATUS')
        result = {}
        for k, v in cursor.fetchall():
            result[k] = v
        cursor.close()
        return result


class ServerSystemVariables(Plugin):

    def __init__(self, **kwargs):
        self.keywords = ['provider']
        print self.__class__.__name__, 'initialising...'

    def generate(self, **kwargs):
        cursor = kwargs['connection'].cursor()
        cursor.execute('SHOW GLOBAL VARIABLES')
        result = {}
        for k, v in cursor.fetchall():
            result[k] = v
        cursor.close()
        return result


class HostProperties(Plugin):

    def __init__(self, **kwargs):
        self.keywords = ['provider']
        print self.__class__.__name__, 'initialising...'

    def _get_total_cores(self):
        f = open('/proc/cpuinfo', 'r')
        c_cpus = 0
        for line in f.readlines():
            if line.startswith('processor'):
                c_cpus += 1
        f.close()
        return c_cpus

    def generate(self, **kwargs):
        result = { 'mem_phys_total': psutil.TOTAL_PHYMEM,
                   'mem_phys_avail': psutil.avail_phymem(),
                   'mem_phys_used' : psutil.used_phymem(),
                   'mem_virt_total': psutil.total_virtmem(),
                   'mem_virt_avail': psutil.avail_virtmem(),
                   'mem_virt_used' : psutil.used_virtmem(),
                   'cpu_cores'     : self._get_total_cores(),
                 }
        return result
