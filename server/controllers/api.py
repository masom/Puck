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
from models import VirtualMachines, Keys

class ApiCall(object):
    exposed = True

class ApiRegistration(ApiCall):

    @cherrypy.tools.json_out()
    def POST(self):
        vm = VirtualMachines.new(ip=cherrypy.request.remote.ip)
        VirtualMachines.add(vm)
        return vm.to_dict()

class ApiKeys(ApiCall):

    @cherrypy.tools.json_out()
    def GET(self):
        keys = Keys.all()
        return dict((k.name, key.to_dict()) for k in keys)


class ApiStatus(ApiCall):

    def PUT(self):
        self._vm.status = cherrypy.request.body.read()

    def GET(self):
        return self._vm.status


class ApiConfig(ApiCall):

    @cherrypy.tools.json_in()
    def POST(self):
        print(cherrypy.request.json)
        print(cherrypy.request.remote)

    @cherrypy.tools.json_out()
    def GET(self):
        return self._vm.config

class ApiEnvironments(ApiCall):

    @cherrypy.tools.json_out()
    def GET(self):
        return self.Environment.get()

class ApiJails(ApiCall):

    @cherrypy.tools.json_out()
    def GET(self, environment=None):
        jails = self.Jail.jails()[environment]

        result = dict()
        for typ, typJails in jails.iteritems():
            result[typ] = dict((jailId, asdict(jailId, jail))
                                    for jailId, jail in typJails)
        return result

class ApiYum(ApiCall):

    @cherrypy.tools.json_out()
    def GET(self, environment=None):
        repos = self.YumRepo.repos()
        if not environment in repos:
            # @TODO: API ERROR HANDLING
            return
        return {'environment': environment, 'data': repos[environment]}

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
