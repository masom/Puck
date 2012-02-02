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
        return self.render("jail_types/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    def add(self, **post):
        if 'jail_type' in post:
            jail_type = JailTypes.new(post)
            if jail_type.validates():
                JailTypes.add(jail_type)
                cherrypy.session['flash'] = "Jail Type successfully added."
                raise cherrypy.HTTPRedirect("/jail_types")
            cherrypy.session['flash'] = "Invalid data."
        env = dict(
            jail_types = JailTypes.all()
        )
        return self.render("jail_types/add.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def view(self, id):
        jail_type = JailTypes.first(id=id)
        env=dict(jail_type = jail_type)
        return self.render("jail_types/view.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def delete(self, id):
        JailTypes.delete(id)
        cherrypy.session['flash'] = "Jail Type deleted."
        raise cherrypy.HTTPRedirect('/jail_types')
