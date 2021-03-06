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
import cherrypy
from libs.controller import *
from models import Keys

class KeysController(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/keys", "Keys")]

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def index(self):
        env = dict(keys=Keys.all())
        return self.render("keys/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def add(self, **post):
        key = Keys.new(name="", key="")
        if post:
            fields = ['name', 'key']
            data = self._get_data('key', fields, post)
            self._set_data(key, data)

            if key.validates() and Keys.add(key):
                cherrypy.session['flash'] = "Key successfully added"
                raise cherrypy.HTTPRedirect("/keys")
            cherrypy.session['flash'] = "Key is not a valid SSH-RSA"

        env = dict(key=key)
        return self.render("keys/add.html", crumbs=self.crumbs, **env)


    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def view(self, name):
        key = Keys.first(name=name)
        env = dict(key=key)
        return self.render("keys/add.html", crumbs=self.crumbs, **env)

