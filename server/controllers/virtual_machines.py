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

class VirtualMachines(Controller):
    crumbs = [
        Crumb("/", "Home"),
        Crumb("/virtual_machines", "Virtual Machines")
    ]

    models = [models.VM]

    @cherrypy.expose
    def index(self):
        vms = self.VM.list()
        env = dict(vms=vms)
        return self.render("virtual_machines/index.html", self.crumbs, **env)

    def running(self):
        vms = self.VM.list()
        instances = self.Image.all()
        return self.render("virtual_machines/running.html", self.crumbs, vms=vms, instances=instances)

    @cherrypy.expose
    def start(self, **post):
        if 'image_id' in post:
            args = dict(
                action="create",
                image_id=post['image_id'],
                credentials=cherrypy.session.get('credentials')
            )
            cherrypy.engine.publish("virtualization", **args)
            cherrypy.session['flash'] = "VM started"
        else:
            cherrypy.sessino['flash'] = 'Missing image id.'

        raise cherrypy.HTTPRedirect("/virtual_machines")

    @cherrypy.expose
    def stop(self, vm_id=None):
        args = dict(
            action="stop",
            id=vm_id,
            credentials=cherrypy.session.get('credentials')
        )
        cherrypy.engine.publish("virtualization", **args)

        cherrypy.session['flash'] = "VM Stopped"
        raise cherrypy.HTTPRedirect("/virtual_machines")
