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
from controllers.base import *
from libs.credentials import Credentials
import models


class Root(Controller):
    crumbs = [Crumb("/", "Home")]
    models = [models.VM]

    def __init__(self, db, lookup):
        Controller.__init__(self, lookup, dict((m, None) for m in self.models))
        self._db = db
        self._routes = {}

    @cherrypy.expose
    def index(self):
        return self.render("index.html", self.crumbs[:-1])

    @cherrypy.expose
    def login(self, **post):
        if post:
            # @TODO actually authenticate. This is a placeholder for now.
            cherrypy.session['credentials'] = Credentials()

        return self.render("login.html", self.crumbs[:-1])

    @cherrypy.expose
    def statuses(self):
        vms = self.VM.list()
        env = dict(vms=vms)
        return self.render("statuses.html", self.crumbs, **env)

    @cherrypy.expose
    def start(self):
        args = dict(action="create", image_id='temp', credentials=cherrypy.session.get('credentials'))
        cherrypy.engine.publish("virtualization", **args)

        cherrypy.session['flash'] = "VM started"
        raise cherrypy.HTTPRedirect("/statuses")

    @cherrypy.expose
    def stop(self, vm_id=None):
        args = dict(action="stop", id=vm_id, credentials=cherrypy.session.get('credentials'))
        cherrypy.engine.publish("virtualization", **args)

        cherrypy.session['flash'] = "VM Stopped"
        raise cherrypy.HTTPRedirect("/statuses")

    def add(self, route, cls):
        self._routes[route] = cls

    def load(self):
        models = set(self.models)
        for cls in self._routes.itervalues():
            models.update(cls.models)
            models.update(*(scls.models for scls in cls.sub))

        models = dict((cls, cls({})) for cls in models)

        for route, cls in self._routes.iteritems():
            need = set(cls.models).union(*[scls.models for scls in cls.sub])
            clsModels = dict((mcls, models[mcls]) for mcls in need)
            setattr(self, route, cls(self._lookup, clsModels))

        for model in self.models:
            setattr(self, model.__name__, models[model])
