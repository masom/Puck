'''
Pixie: FreeBSD virtualization guest configuration client
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
import cherrypy, os, sys, time

from lib.vm import VM
from lib.puck import Puck
from lib.jails import *
from lib.setup_plugin import SetupPlugin

from lib.controller import Controller
from controllers.configuration import ConfigurationController
from controllers.setup import SetupController


class Root(Controller):

    def __init__(self, vm):
        self._vm = vm

    @cherrypy.expose
    def index(self):
        env = dict(
            VM=self._vm
        )
        return self.render('/index.html', **env)

puck = Puck()
vm = puck.getVM()

root = Root(vm)
root.configure = ConfigurationController(vm)
root.setup = SetupController(vm)

if __name__ == "__main__":
    conf =  {'/' : 
                {
                    'request.dispatch' : cherrypy.dispatch.Dispatcher(),
                    'tools.sessions.on' : True
                }
            }

    cherrypy.engine.vmsetup = SetupPlugin(vm, cherrypy.engine)
    cherrypy.engine.vmsetup.subscribe()

    cherrypy.quickstart(root, '/', conf)
