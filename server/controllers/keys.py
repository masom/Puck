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

class Keys(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/keys", "Keys")]

    @cherrypy.expose
    def index(self):
        env = dict(keys=self.Key.keys())
        return self.render("keys/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    def add(self, **post):
        key = self.Key.Table(None, None)
        if post:
            keystr = post['key'].split()
            if '\n' in post['key']:
                cherrypy.session['flash'] = "Key is invalid"
            elif len(keystr) not in (2,3):
                cherrypy.session['flash'] = "Key is invalid"
            else:
                self.Key.new(post)
                cherrypy.session['flash'] = "Key successfully added"
                raise cherrypy.HTTPRedirect("/keys")
            key = self.Key.Table(post['name'], post['key'])


        env = dict(key=key, disabled=False)
        return self.render("keys/add.html", crumbs=self.crumbs, **env)


    @cherrypy.expose
    def view(self, key_id):
        key = self.Key.get(key_id)
        env = dict(key=key, disabled=True)
        return self.render("keys/add.html", crumbs=self.crumbs, **env)

