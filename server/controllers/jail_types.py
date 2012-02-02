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
from models import JailTypes

class JailTypesController(Controller):
    crumbs = [Crumb("/", "Home"), Crumb('/jail_types', 'Jail Types')]

    @cherrypy.expose
    def index(self):
        env = dict(jail_types=JailTypes.all())
        return self.render("/jail_types/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    def add(self, **post):
        jail_type = JailTypes.new()
        if post:
            data = dict((k.split(".", 1)[1], post[k]) for k in post if k.startswith('jail_type.'))
            for k in data:
                setattr(jail_type, k, data[k])

            if jail_type.validates():
                JailTypes.add(jail_type)
                cherrypy.session['flash'] = "Jail Type successfully added."
                raise cherrypy.HTTPRedirect("/jail_types")

            cherrypy.session['flash'] = "Invalid data."

        env = dict(
            jail_type = jail_type
        )
        return self.render("/jail_types/add.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def view(self, id):
        jail_type = JailTypes.first(id=id)
        env=dict(jail_type = jail_type)
        return self.render("/jail_types/view.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def delete(self, id):
        jail = JailTypes.first(id=id)
        msg = "The jail could not be deleted."
        if jail:
            if JailTypes.delete(jail):
                msg = "Jail Type deleted."

        cherrypy.session['flash'] = msg

        raise cherrypy.HTTPRedirect('/jail_types')

    def _validatePost(self, post):
        attrs = ['id', 'name', 'ip']
        for a in attrs:
            if not a in post:
                return False
        return True

