'''
Puck: FreeBSD virtualization guest configuration server
Copyright (C) 2011  The Hotel Communication Network inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import os.path

import cherrypy
from mako.lookup   import TemplateLookup

from controllers.base import *
import plugins.vmLauncher as vmLauncher


class Root(Controller):
    plugins = [vmLauncher.Launcher]

    def __init__(self, db, templatedir):
        lookup  = TemplateLookup(
                            directories=[os.path.join(templatedir, relative) 
                                            for relative in ["views"]]
                        )

        Controller.__init__(self, lookup, {})
        self._db = db


        self._routes = {}
        
    @cherrypy.expose
    def index(self):
        return self.render("index.html")

    @cherrypy.expose
    def statuses(self, a=None):
        return "Nope Nope Nope"

    @cherrypy.expose
    def start(self):
        self.launcher.launch()
        cherrypy.session['flash'] = "VM started"
        raise cherrypy.HTTPRedirect("/statuses")

    def add(self, route, cls):
        self._routes[route] = cls

    def load(self):
        models = set()
        for cls in self._routes.itervalues():
            models.update(cls.models)
            models.update(*(scls.models for scls in cls.sub))

        models = dict((cls, cls({})) for cls in models)

        for route, cls in self._routes.iteritems():
            need = set(cls.models).union(*[scls.models for scls in cls.sub])
            clsModels = dict((mcls, models[mcls]) for mcls in need)
            setattr(self, route, cls(self._lookup, clsModels))

        for plugin in self.plugins:
            clsModels = dict((mcls, models[mcls]) for mcls in plugin.models)
            setattr(self, plugin.__name__.lower(), plugin(clsModels))
