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
import models
from models import Users

class RootController(Controller):
    crumbs = [Crumb("/", "Home")]

    def __init__(self, lookup):
        Controller.__init__(self, lookup)
        self._lookup = lookup
        self._routes = {}

    @cherrypy.expose
    @cherrypy.tools.myauth()
    def index(self):
        return self.render("index.html", self.crumbs[:-1])

    @cherrypy.expose
    def login(self, **post):
        if post:
            self._login(post)
        return self.render("login.html", self.crumbs[:-1])

    @cherrypy.expose
    def logout(self, **post):
        cherrypy.session.delete()
        raise cherrypy.HTTPRedirect("/login")

    def add(self, route, cls):
        self._routes[route] = cls

    def load(self):
        [setattr(self, route, self._routes[route](self._lookup)) for route in self._routes]

    def _login(self, post):
            fields = ['user.username', 'user.password']
            for f in fields:
                if not f in post:
                    cherrypy.session['flash'] = "Invalid form data."
                    return False

            hash_password = Users.hash_password(post['user.password'])
            user = Users.first(username=post['user.username'], password=hash_password)

            if not user:
                cherrypy.session['flash'] = 'Invalid username or password.'
                return False
            creds = user.generate_auth()

            cherrypy.session['user.id'] = user.id
            cherrypy.session['user.group'] = user.user_group
            cherrypy.session['credentials'] = creds
            raise cherrypy.HTTPRedirect('/index')
