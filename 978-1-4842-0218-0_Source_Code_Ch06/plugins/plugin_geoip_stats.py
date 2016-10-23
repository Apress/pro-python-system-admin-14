#!/usr/bin/env python

from manager import Plugin
from operator import itemgetter
import GeoIP
import shapefile
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.basemap import Basemap
from matplotlib.collections import LineCollection
from matplotlib import cm


class GeoIPStats(Plugin):

    def __init__(self, **kwargs):
        self.gi = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)
        self.countries = {}

    def process(self, **kwargs):
        if 'remote_host' in kwargs:
            country = self.gi.country_name_by_addr(kwargs['remote_host'])
            if country in self.countries:
                self.countries[country] += 1
            else:
                self.countries[country] = 1

    def report(self, **kwargs):
        print "== Requests by country =="
        for (country, count) in sorted(self.countries.iteritems(), key=itemgetter(1), reverse=True):
            print " %10d: %s" % (count, country)
        generate_map(self.countries)


def generate_map(countries):

    # Initialize plotting area, set the boundaries and add a sub-plot on which
    # we are going to plot the map
    fig = plt.figure(figsize=(11.7, 8.3))
    plt.subplots_adjust(left=0.05,right=0.95,top=0.90,bottom=0.05,wspace=0.15,hspace=0.05)
    ax = plt.subplot(111)

    # Initialize the basemap, set the resolution, projection type and the viewport
    bm = Basemap(resolution='i', projection='robin', lon_0=0)
    
    # Tell basemap how to draw the countries (built-in shapes), draw parallels and meridians
    # and color in the water
    bm.drawcountries(linewidth=0.5)
    bm.drawparallels(np.arange(-90., 120., 30.))
    bm.drawmeridians(np.arange(0., 360., 60.))
    bm.drawmapboundary(fill_color='aqua')

    # Open the countries shapefile and read the shape and attribute information
    r = shapefile.Reader('world_borders/TM_WORLD_BORDERS-0.3.shp')
    shapes = r.shapes()
    records = r.records()

    # Iterate through all records (attributes) and shapes (countries)
    for record, shape in zip(records, shapes):

        # Extract longitude and latitude values into two separate arrays then
        # project the coordinates onto the map projection and transpose the array, so that
        # the data variable contains (lon, lat) pairs in the list.
        # Basically, the following two lines convert the initial data
        #  [ [lon_original_1, lat_original_1], [lon_original_2, lat_original_2], ... ]
        # into projected data
        #  [ [lon_projected_1, lat_projected_1, [lon_projected_2, lat_projected_2], ... ]
        #
        # Note: Calling baseshape object with the coordinates as an argument returns the
        #       projection of those coordinates
        lon_array, lat_array = zip(*shape.points)
        data = np.array(bm(lon_array, lat_array)).T

        # Next we will create groups of points by splitting the shape.points according to
        # the indices provided in shape.parts

        if len(shape.parts) == 1:
            # If the shape has only one part, then we have only one group. Easy.
            groups = [data,]
        else:
            # If we have more than one part ...
            groups = []
            for i in range(1, len(shape.parts)):
                # We iterate through all parts, and find their start and end positions
                index_start = shape.parts[i-1]
                index_end = shape.parts[i]
                # Then we copy all point between two indices into their own group and append
                # that group to the list
                groups.append(data[index_start:index_end])
            # Last group starts at the last index and finishes at the end of the points list
            groups.append(data[index_end:])

        # Create a collection of lines provided the group of points. Each group represents a line.
        lines = LineCollection(groups, antialiaseds=(1,))
        # We then select a color from a color map (in this instance all Reds)
        # The intensity of the selected color is proportional to the number of requests.
        # Color map accepts values from 0 to 1, therefore we need to normalize our request count
        # figures, so that the max number of requests is 1, and the rest is proportionally spread
        # in the range from 0 to 1.
        max_value = float(max(countries.values()))
        country_name = record[4]

        requests = countries.get(country_name, 0)
        requests_norm = requests / max_value

        lines.set_facecolors(cm.Reds(requests_norm))

        # Finally we set the border color to be black and add the shape to the sub-plot
        lines.set_edgecolors('k')
        lines.set_linewidth(0.1)
        ax.add_collection(lines)

    # Once we are ready, we save the resulting picture
    plt.savefig('requests_per_country.png', dpi=300)

