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
from models import Environments

class EnvironmentsController(Controller):
    #coppied this from the environments controller
    crumbs = [Crumb("/", "Home"), Crumb('/environments', 'Environments')]
    
    @cherrypy.expose
    def index(self):
        env = dict(environments=Environments.all())
        return self.render("/environments/index.html", crumbs=self.crumbs[:-1], **env)

    
    @cherrypy.expose
    def add(self, **post):
        environment = Environments.new(id="", name="")
        if post:
            fields = ['id', 'name' ]
            data = self._get_data('environment', fields, post)
            self._set_data(environment, data)

            if environment.validates() and Environments.add(environment):
                cherrypy.session['flash'] = "Environment successfully added."
                raise cherrypy.HTTPRedirect("/environments")

            cherrypy.session['flash'] = "Invalid data."

        env = dict(
            environment = environment
        )
        return self.render("/environments/add.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def edit(self, id, **post):
        environment = Environments.first(id=id)
        if not environment:
            cherrypy.session['flash'] = "404 Environment Not Found"
            raise cherrypy.HTTPRedirect('/environments')

        if post:
            fields = ['name']
            data = self._get_data('environment', fields, post)
            if environment.update(data, fields):
                cherrypy.session['flash'] = "Environment successfully updated."
                raise cherrypy.HTTPRedirect('/environments')

        env=dict(environment = environment)
        return self.render("/environments/edit.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def delete(self, id):
        environment = Environments.first(id=id)
        msg = "The jail could not be deleted."
        if environment:
            if Environments.delete(jail):
                msg = "Jail Type deleted."

        cherrypy.session['flash'] = msg

        raise cherrypy.HTTPRedirect('/environments')

    def _validatePost(self, post):
        attrs = ['id', 'name', 'ip']
        for a in attrs:
            if not a in post:
                return False
        return True
