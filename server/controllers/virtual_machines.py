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
from models import VirtualMachines, Images, InstanceTypes
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
            instance_types=InstanceTypes.all()
        )
        return self.render("virtual_machines/index.html", self.crumbs, **env)

    @cherrypy.expose
    def running(self):
        vms = VirtualMachines.all()
        images = Images.all()
        virtual_machines = VirtualMachines.all()
        args = dict(
            action="status",
            credentials=cherrypy.session.get('credentials')
        )
        instances = cherrypy.engine.publish("virtualization", **args).pop()
        env = dict(
                vms=vms,
                instances=instances,
                images=images,
                virtual_machines=virtual_machines
        )
        return self.render("virtual_machines/running.html", self.crumbs,**env)

    @cherrypy.expose
    def start(self, **post):
        if post:
            self._validate_start_post_data(post)
            creds = cherrypy.session.get('credentials')

            image = Images.first(id=post['image.id'])
            instance_type = self._get_instance_type(post)

            self._validate_start_args(image, instance_type)

            vm = VirtualMachines.new(
                    image_id = image.id,
                    instance_type_id = instance_type.id,
                    status="new"
            )

            args = dict(
                action="create",
                image_id=image.backend_id,
                instance_type=instance_type.id,
                credentials=creds
            )

            instance = cherrypy.engine.publish("virtualization", **args).pop()

            if instance is False:
                cherrypy.session['flash'] = 'The virtual machine could not be started.'
            else:
                cherrypy.session['flash'] = "VM started"

            vm.instance_id = instance.id
            vm.user = creds.name
            if not VirtualMachines.add(vm):
                cherrypy.session['flash'] = "VM Started but an error occured while saving virtual machine."

        else:
            cherrypy.session['flash'] = 'Missing image id.'

        raise cherrypy.HTTPRedirect("/virtual_machines")

    def _get_instance_type(self, post):
        if post['instance_type.id'].isdigit():
            id = int(post['instance_type.id'])
        else:
            id = post['instance_type.id']
        return InstanceTypes.first(id=id)

    def _validate_start_post_data(self, post):
        for r in ['image.id', 'instance_type.id']:
            if not r in post:
                cherrypy.session['flash'] = 'Missing image or instance id.'
                raise cherrypy.HTTPRedirect("/virtual_machines")

    def _validate_start_args(self, image, instance_type):
        if not image or not instance_type:
            cherrypy.session['flash'] = 'Invalid image or instance type.'
            raise cherrypy.HTTPRedirect("/virtual_machines")

        if not image.backend_id:
            cherrypy.session['flash'] = 'Invalid image record.'
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

