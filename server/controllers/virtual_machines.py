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
    @cherrypy.tools.myauth()
    def add_public_ip(self, id):
        creds=cherrypy.session.get('credentials')
        vm = self._get_vm(id)
        ip = vm.add_public_ip(creds)
        if ip:
            msg = 'IP added: %s' % ip
        else:
            msg = 'An IP could not be added to the instance.'
        cherrypy.session['flash'] = msg
        raise cherrypy.HTTPRedirect('/virtual_machines/running')

    @cherrypy.expose
    @cherrypy.tools.myauth()
    def index(self):
        user_id = cherrypy.session.get('user.id')
        vms = VirtualMachines.find(user_id=user_id)
        env = dict(
            virtual_machines=vms,
            images=Images.all(),
            instance_types=InstanceTypes.all()
        )
        return self.render("virtual_machines/index.html", self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth()
    def running(self):
        creds = cherrypy.session.get('credentials')
        vms = VirtualMachines.all()
        images = Images.all()
        instances = VirtualMachines.get_instances(creds)
        env = dict(
            virtual_machines=vms,
            instances=instances,
            images=images,
        )

        return self.render("virtual_machines/running.html", self.crumbs,**env)

    @cherrypy.expose
    @cherrypy.tools.myauth()
    def start(self, **post):
        if post:
            self._validate_start_post_data(post)
            creds = cherrypy.session.get('credentials')

            image = Images.first(id=post['image.id'])
            instance_type = self._get_instance_type(post)

            self._validate_start_args(image, instance_type)

            vm = VirtualMachines.new(status="new")

            if VirtualMachines.add(vm):
                if not vm.start_instance(image, instance_type, creds):
                    cherrypy.session['flash'] = 'The virtual machine could not be started.'
                    raise cherrypy.HTTPRedirect("/virtual_machines")
        else:
            cherrypy.session['flash'] = 'Missing image id.'

        raise cherrypy.HTTPRedirect("/virtual_machines")

    @cherrypy.expose
    @cherrypy.tools.myauth()
    def restart(self, id=None):
        creds=cherrypy.session.get('credentials')
        vm = self._get_vm(id)

        if vm.restart_instance(creds):
            cherrypy.session['flash'] = 'VM restarting'
        else:
            cherrypy.session['flash'] = 'The vm could not be restarted.'
        raise cherrypy.HTTPRedirect("/virtual_machines")

    @cherrypy.expose
    @cherrypy.tools.myauth()
    def stop(self, id=None):
        creds = cherrypy.session.get('credentials')
        vm = self._get_vm(id)

        if vm.stop_instance():
            cherrypy.session['flash'] = "VM Stopped"
        else:
            cherrypy.session['flash'] = 'The vm could not be stopped.'
        raise cherrypy.HTTPRedirect("/virtual_machines")

    @cherrypy.expose
    @cherrypy.tools.myauth()
    def delete(self, id=None):
        creds = cherrypy.session.get('credentials')

        vm = self._get_vm(id)
        if vm.instance_id:
            try:
                if not vm.delete_instance(creds):
                    msg = 'The virtual machine instance could not be deleted.'
                    cherrypy.session['flash'] = msg
                    raise cherrypy.HTTPRedirect('/virtual_machines')
            except KeyError, e:
                pass

        VirtualMachines.delete(vm)
        cherrypy.session['flash'] = 'Virtual machine deleted.'
        raise cherrypy.HTTPRedirect('/virtual_machines')

    def _get_vm(self, id):
        vm = VirtualMachines.first(id=id)
        if not vm:
            cherrypy.session['flash'] = "Invalid virtual machine."
            raise cherrypy.HTTPRedirect('/virtual_machines')
        return vm

    def _get_instance_type(self, post):
        if post['instance_type.id'].isdigit():
            id = int(post['instance_type.id'])
        else:
            id = post['instance_type.id']

        return InstanceTypes.first(id=str(id))

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

