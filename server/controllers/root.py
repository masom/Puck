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
from libs.controller import *
from libs.credentials import Credentials


class Root(Controller):
    crumbs = [Crumb("/", "Home")]

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
            raise cherrypy.HTTPRedirect('/index')
        return self.render("login.html", self.crumbs[:-1])

    @cherrypy.expose
    def logout(self, **post):
        cherrypy.session['credentials'] = None
        raise cherrypy.HTTPRedirect("/login")
    def add(self, route, cls):
        self._routes[route] = cls
