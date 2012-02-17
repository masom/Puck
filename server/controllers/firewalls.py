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
from models import Firewalls

class FirewallsController(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/firewalls", "Firewalls")]

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def index(self):
        env = dict(
            firewalls=Firewalls.all()
        )
        return self.render("/firewalls/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def add(self, **post):
        firewall = Firewalls.new(data="", name="")
        if post:
            fields = ['data', 'name']
            data = self._get_data('firewall', fields, post)
            self._set_data(firewall, data)

            if Firewalls.add(firewall):
                cherrypy.session['flash'] = "Firewall successfully added"
                raise cherrypy.HTTPRedirect("/firewalls/index")
            cherrypy.session['flash'] = "The firewall data contains errors."

        firewalls = Firewalls.all()
        return self.render("/firewalls/add.html", crumbs=self.crumbs, firewall=firewall)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def edit(self, id, **post):

        firewall = Firewalls.first(id=id)
        if not firewall:
            raise cherrypy.HTTPRedirect('/firewalls')

        if post:
            fields = ['data', 'name']
            data = self._get_data('firewall', fields, post)
            firewall.update(data, fields)
            raise cherrypy.HTTPRedirect('/firewalls/view/%s' % id)

        env = dict(
            firewall=firewall,
        )
        return self.render("/firewalls/edit.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def view(self, id):
        firewall = Firewalls.first(id=id)
        if not firewall:
            cherrypy.session['flash'] = '404 Firewall Not Found'
            raise cherrypy.HTTPRedirect('/firewalls/index')
        env = dict(
            firewall=firewall,
        )
        return self.render("/firewalls/view.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def delete(self, environment):
        firewall = Firewalls.first(environment=environment)
        msg = "The firewall could not be deleted."
        if firewall:
            if Firewalls.delete(firewall):
                msg = "Firewall deleted."

        cherrypy.session['flash'] = msg

        raise cherrypy.HTTPRedirect('/firewalls')

