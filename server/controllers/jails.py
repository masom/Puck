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
from models import Jails, JailTypes, Environments

class JailsController(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/jails", "Jails")]

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def index(self):
        env = dict(jails=Jails.all())
        return self.render("jails/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def add(self, **post):
        jail = Jails.new(id="", url="", name="", ip="", jail_type="", netmask="", environment="")
        if post:
            fields = ['name', 'url', 'ip', 'jail_type', 'netmask', 'environment']
            data = self._get_data('jail', fields, post)
            self._set_data(jail, data)

            if jail.validates() and Jails.add(jail):
                cherrypy.session['flash'] = "Jail successfully added"
                raise cherrypy.HTTPRedirect("/jails")
            cherrypy.session['flash'] = "The jail could not be created."

        env = dict(
                environments=Environments.all(),
                jailTypes=JailTypes.all(),
                jail=jail
        )

        return self.render("jails/add.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def edit(self, id, **post):
        jail = Jails.first(id=id)
        if not jail:
            cherrpy.session['flash'] = '404 Jail Not Found'
            raise cherrypy.HTTPRedirect('/jails/index')

        if post:
            fields = ['name', 'url', 'ip', 'jail_type', 'netmask', 'environment']
            data = self._get_data('jail', fields, post)
            tmp = Jails.new()
            self._set_data(tmp, data)
            if tmp.validates() and jail.update(data, fields):
                cherrypy.session['flash'] = "Jail successfully updated."
                raise cherrypy.HTTPRedirect("/jails")
            cherrypy.session['flash'] = "The jail could not be updated."

        env = dict(
                environments=Environments.all(),
                jailTypes=JailTypes.all(),
                jail=jail
        )

        return self.render("jails/edit.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def delete(self, id):
        jail = Jails.first(id=id)
        if not jail:
            cherrypy.session['flash'] = '404 Jail Not found'
        else:
            Jails.delete(jail)
            cherrypy.session['flash'] = "Jail successfully deleted"
        raise cherrypy.HTTPRedirect("/jails")
