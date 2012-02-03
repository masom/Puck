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
from models import VirtualMachines, Images
import models,pickle
class VirtualMachinesController(Controller):
    crumbs = [
        Crumb("/", "Home"),
        Crumb("/virtual_machines", "Virtual Machines")
    ]

    @cherrypy.expose
    def index(self):
        #Images.add(Images.new(id="test", name="test"))
        env = dict(
            virtual_machines=VirtualMachines.all(),
            images=Images.all(),
            instance_types=self._get_instance_types()
        )
        return self.render("virtual_machines/index.html", self.crumbs, **env)

    @cherrypy.expose
    def running(self):
        vms = VirtualMachines.all()
        images = Images.all()
        args = dict(
            action="status",
            credentials=cherrypy.session.get('credentials')
        )
        instances = cherrypy.engine.publish("virtualization", **args)
        return self.render("virtual_machines/running.html", self.crumbs, vms=vms, instances=instances, images=images)

    @cherrypy.expose
    def start(self, **post):
        if post:
            image = Images.find(id=post['image.id'])
            if not image:
                cherrypy.session['flash'] = 'Missing image id.'
                raise cherrypy.HTTPRedirect("/virtual_machines")

            args = dict(
                action="create",
                image_id=post['image.id'],
                credentials=cherrypy.session.get('credentials')
            )
            cherrypy.engine.publish("virtualization", **args)
            cherrypy.session['flash'] = "VM started"
        else:
            cherrypy.session['flash'] = 'Missing image id.'

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

    def _get_instance_types(self):
        data={
                'nova_url':"http://10.0.254.100:8774/v1.0/",
                'nova_username':"msamson",
                'nova_api_key':"e39caef5-f357-40d9-9a43-21cbe969a07b",
                'nova_project_id':"mproj"
            }
        cred = models.Credential(
            id="test",
            name="martin samson",
            data = pickle.dumps(data)
        )
        cherrypy.session['credentials'] = cred
        args = dict(
            action = "instance_types",
            credentials=cherrypy.session.get('credentials')
        )
        instance_types = cherrypy.engine.publish("virtualization", **args).pop()

        print instance_types
