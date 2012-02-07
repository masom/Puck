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
from models import VirtualMachines, Keys, Environments, Jails, YumRepositories
import json

class ApiCall(object):
    exposed = True

class ApiRegistration(ApiCall):

    @cherrypy.tools.json_out()
    def POST(self):
        # TODO Check if the ip already has an assigned VM
        # We might have to figure a way to generate a unique id on the VM side
        vm = VirtualMachines.new(ip=cherrypy.request.remote.ip)
        VirtualMachines.add(vm)
        return vm.to_dict()
    @cherrypy.tools.json_out()
    def GET(self, id):
        vm = VirtualMachines.first(id=id)
        if not vm:
            raise cherrypy.HTTPError(status=404)

        return vm.to_dict()

class ApiKeys(ApiCall):

    @cherrypy.tools.json_out()
    def GET(self):
        keys = Keys.all()
        return dict((k.name, k.to_dict()) for k in keys)


class ApiStatus(ApiCall):

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def PUT(self, id):
        vm = VirtualMachines.first(id=id)
        if not vm:
            raise cherrypy.HTTPError(status=404)

        data = cherrypy.request.json
        for k in ['id', 'status']:
            if not data.has_key(k):
                raise cherrypy.HTTPError(status=400)

        if not id == data['id']:
            raise cherrypy.HTTPError(status=400)

        if not vm.update(data, ['status']):
            raise cherrypy.HTTPError(status=500)

        return {'status': 200, 'message': 'Status updated.'}

class ApiConfig(ApiCall):

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, id, **post):

        vm = VirtualMachines.first(id=id)
        if not vm:
            raise cherrypy.HTTPError(status=404)

        try:
            config = json.loads(vm.config)
        except (ValueError,TypeError):
            config = {}

        for k in cherrypy.request.json:
            value = cherrypy.request.json[k]
            if value is None:
                del config[k]
                continue
            config[k] = value

        data = {'config': json.dumps(config)}
        vm.update(data, ['config'])
        return {'status': 200, 'message': 'Configuration updated.'}

    @cherrypy.tools.json_out()
    def GET(self, id):
        vm = VirtualMachines.first(id=id)
        if not vm:
            raise cherrypy.HTTPError(status=404)

        try:
            config = json.loads(vm.config)
        except (ValueError,TypeError):
            return None
        return config

class ApiEnvironments(ApiCall):

    @cherrypy.tools.json_out()
    def GET(self):
        envs = Environments.all()
        return [e.to_dict() for e in envs]

class ApiJails(ApiCall):

    @cherrypy.tools.json_out()
    def GET(self, environment=None):
        jails = Jails.find(environment=environment)

        result = {}
        for jail in jails:
            if not result.has_key(jail.jail_type):
                result[jail.jail_type] = []
            result[jail.jail_type].append(jail.to_dict())
        return result

class ApiYum(ApiCall):

    @cherrypy.tools.json_out()
    def GET(self, environment=None):
        repo = YumRepositories.first(environment=environment)
        if not repo:
            return None
        return repo.to_dict()

class Api(Controller):
    def __init__(self, lookup):
        Controller.__init__(self, None)

        self.registration = ApiRegistration()
        self.keys = ApiKeys()
        self.status = ApiStatus()
        self.config = ApiConfig()
        self.environments = ApiEnvironments()
        self.jails = ApiJails()
        self.yum_repo = ApiYum()
