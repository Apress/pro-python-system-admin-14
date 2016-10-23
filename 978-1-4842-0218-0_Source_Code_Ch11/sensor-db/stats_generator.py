#!/usr/bin/env python

import sqlite3
import dateutil

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from jinja2 import Environment, FileSystemLoader


DATABASE='monitor.db'
#LOCATION='/home/rytis/public_html/'
LOCATION='/Users/rytis/Sites/'
TIMESCALES=(1, 7, 30)

class SiteGenerator:
    def __init__(self, db_name, location, tpl_env):
        self.location = location
        self.tpl_env = tpl_env
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.hosts = []
        self._get_all_hosts()

    def generate_site_pages(self):
        self._generate_hosts_view()
        self._generate_host_details_contents()

    def _get_all_hosts(self):
        for h in self.conn.execute("SELECT * FROM host"):
            host_entry = list(h)
            query_str = """ SELECT hostprobe.id,
                                   probe.name,
                                   COALESCE(hostprobe.warning, probe.warning),
                                   COALESCE(hostprobe.error, probe.error)
                            FROM   probe,
                                   hostprobe
                            WHERE  probe.id = hostprobe.probe_id AND
                                   hostprobe.host_id = ?
                        """
            probes = self.conn.execute(query_str, (h[0],)).fetchall()
            host_entry.append(probes)
            self.hosts.append(host_entry)

    def _generate_hosts_view(self):
        t = self.tpl_env.get_template('index.template')
        f = open("%s/index.html" % self.location, 'w')
        f.write(t.render({'hosts': self.hosts}))
        f.close()

    def _generate_host_details_contents(self):
        for host in self.hosts:
            # host[0] - id
            # host[1] - name
            # host[2] - address
            # host[3] - port
            # host[4] - probelist
            for probe in host[4]:
                # probe[0] - (hostprobe_)id
                # probe[1] - probe name
                # probe[2] - warning threshold
                # probe[3] - error threshold
                sampling_rate = self.conn.execute("SELECT probeinterval FROM probingschedule WHERE hostprobe_id=?", 
                                                  (probe[0],)).fetchone()[0]
                for scale in TIMESCALES:
                    self._plot_time_graph(probe[0], 
                                          24 * 60 * scale,
                                          sampling_rate,
                                          "%s - %s (scale: %s day(s))" % (host[1], probe[1], scale),
                                          "plot_%s_%s.png" % (probe[0], scale),
                                          warn = probe[2],
                                          err  = probe[3]
                                         )
                self._generate_host_probe_details(host, probe)
            for scale in TIMESCALES:
                self._generate_host_scale_details(host, scale)
            self._generate_host_toc(host)


    def _generate_host_toc(self, host):
        probe_sa = {}
        for probe in host[4]:
            probe_sa[probe[1]] = {}
            for scale in TIMESCALES:
                probe_sa[probe[1]][scale] = self._calculate_service_availability(probe, scale)
        t = self.tpl_env.get_template('host.template')
        f = open("%s/host_%s_details.html" % (self.location, host[0]), 'w')
        f.write(t.render({ 'host': host,
                           'timescales': TIMESCALES,
                           'probe_sa': probe_sa,
                         }))
        f.close()


    def _calculate_service_availability(self, probe, scale):
        sa_warn = None
        sa_err  = None
        sampling_rate = self.conn.execute("SELECT probeinterval FROM probingschedule WHERE hostprobe_id=?",
                                          (probe[0],)).fetchone()[0]
        records_to_read = int(24 * 60 * scale / sampling_rate)
        query_str = """SELECT count(*) 
                         FROM (SELECT probe_value 
                                 FROM probereading
                                WHERE hostprobe_id=? 
                                LIMIT ?)
                        WHERE probe_value > ?"""
        if probe[2]:    # calculate only if the warning threshold is set
            warning_hits = self.conn.execute(query_str, (probe[0], records_to_read, probe[2],)).fetchone()[0]
            sa_warn = float(warning_hits) / records_to_read
        if probe[3]:    # calculate only if the error threshold is set
            error_hits   = self.conn.execute(query_str, (probe[0], records_to_read, probe[3],)).fetchone()[0]
            sa_err  = float(error_hits) / records_to_read
        return (sa_warn, sa_err)


    def _generate_host_probe_details(self, host_struct, probe_struct):
        # 1) host -> probe -> all scales (host_probe_details)
        t = self.tpl_env.get_template('host_probe_details.template')
        f = open("%s/hpd_%s.html" % (self.location, probe_struct[0]), 'w')
        images = []
        for scale in TIMESCALES:
            images.append([ scale,
                            "plot_%s_%s.png" % (probe_struct[0], scale),
                          ])
        f.write(t.render({'host': host_struct,
                          'probe': probe_struct,
                          'images': images,
                         }))
        f.close()

    def _generate_host_scale_details(self, host_struct, scale):
        # 2) host -> scale -> all probes (host_scale_details)
        t = self.tpl_env.get_template('host_scale_details.template')
        f = open("%s/hsd_%s_%s.html" % (self.location, host_struct[0], scale), 'w')
        images = []
        for probe in host_struct[4]:
            images.append([ probe[1],
                            "plot_%s_%s.png" % (probe[0], scale),
                          ])
        f.write(t.render({'host': host_struct,
                          'scale': scale,
                          'images': images,
                         }))
        f.close()

    def _plot_time_graph(self, hostprobe_id, time_window, sampling_rate, plot_title, plot_file_name, warn=None, err=None):
        records_to_read = int(time_window / sampling_rate)
        records = self.conn.execute("SELECT timestamp, probe_value FROM probereading WHERE hostprobe_id=? LIMIT ?", 
                                    (hostprobe_id, records_to_read)).fetchall()
        time_array, val_array = zip(*records)

        mean = np.mean(val_array)
        std = np.std(val_array)
        warning_val = mean + 3*std
        error_val = mean + 4*std

        data_y = np.array(val_array)
        data_x = np.arange(len(data_y))
        print dateutil.parser
        data_time = [dateutil.parser.parse(s) for s in time_array]
        data_xtime = matplotlib.dates.date2num(data_time)
        a, b = np.polyfit(data_x, data_y, 1)
        matplotlib.rcParams['font.size'] = 10
        fig = plt.figure(figsize=(8,4))
        ax = fig.add_subplot(1, 1, 1)
        ax.set_title(plot_title + "\nMean: %.2f, Std Dev: %.2f, Warn Lvl: %.2f, Err Lvl: %.2f" % (mean, std, warning_val, error_val))
        ax.plot_date(data_xtime, data_y, 'b')
        ax.plot_date(data_xtime, data_x * a + b, color='black', linewidth=3, marker='None', linestyle='-', alpha=0.5)
        fig.autofmt_xdate()
        if warn:
            ax.axhline(warn, color='orange', linestyle='--', linewidth=2, alpha=0.7)
        if err:
            ax.axhline(err, color='red', linestyle='--', linewidth=2, alpha=0.7)
        ax.grid(True)
        plt.savefig("%s/%s" % (self.location, plot_file_name))


def main():
    fs_loader = FileSystemLoader('templates/')
    tpl_env = Environment(loader=fs_loader)
    sg = SiteGenerator(DATABASE, LOCATION, tpl_env)
    sg.generate_site_pages()


if __name__ == '__main__':
    main()
