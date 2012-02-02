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
from controllers.base import *
import models


class Jails(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/jails", "Jails")]

    models = [models.Jail, models.Environment]

    def hash(self):
        return self.Jail.jails()

    @cherrypy.expose
    def index(self):
        env = dict(jails=self.Jail.jails())
        return self.render("jails/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    def add(self, **post):
        if post:
            self.Jail.new(post)
            cherrypy.session['flash'] = "Jail successfully added"
            raise cherrypy.HTTPRedirect("/jails")

        env = dict(
                environments=self.Environment.get().items(),
                jailTypes=self.Jail.types()
        )
        return self.render("jails/add.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def view(self, jail_id):
        jail = self.Jail.get(jail_id)
        env = dict(jail=jail)
        return self.render("jails/view.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def delete(self, jail_id):
        self.Jail.delete(jail_id)

        cherrypy.session['flash'] = "Jail successfully deleted"
        raise cherrypy.HTTPRedirect("/jails")
