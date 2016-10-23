#!/usr/bin/env python

import cherrypy
from cherrypy import _cptools

class Root(_cptools.XMLRPCController):
    @cherrypy.expose
    def hello(selfi, name):
        return "Hello, %s" % name

cherrypy.quickstart(Root(), '/')
