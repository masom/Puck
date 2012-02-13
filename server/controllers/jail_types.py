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
    @cherrypy.tools.myauth(groups=['admin'])
    def index(self):
        env = dict(jail_types=JailTypes.all())
        return self.render("/jail_types/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def add(self, **post):
        jail_type = JailTypes.new(id="", ip="", netmask="")
        if post:
            fields = ['id', 'ip', 'netmask' ]
            data = self._get_data('jail_type', fields, post)
            self._set_data(jail_type, data)

            if jail_type.validates() and JailTypes.add(jail_type):
                cherrypy.session['flash'] = "Jail Type successfully added."
                raise cherrypy.HTTPRedirect("/jail_types")

            cherrypy.session['flash'] = "Invalid data."

        env = dict(
            jail_type = jail_type
        )
        return self.render("/jail_types/add.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def edit(self, id, **post):
        jail_type = JailTypes.first(id=id)
        if not jail_type:
            cherrypy.session['flash'] = "404 Jail Type Not Found"
            raise cherrypy.HTTPRedirect('/jail_types')

        if post:
            fields = ['ip', 'netmask']
            data = self._get_data('jail_type', fields, post)
            if jail_type.update(data, fields):
                cherrypy.session['flash'] = "Jail Type successfully updated."
                raise cherrypy.HTTPRedirect('/jail_types')

        env=dict(jail_type = jail_type)
        return self.render("/jail_types/edit.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
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

