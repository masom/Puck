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

if not __name__ == "__main__":
    raise SystemError("Pixie cannot be imported.")

import os, sys, time

if not sys.version_info >= (2,7):
    sys.exit("Python 2.7 is required for Pixie.")

if not os.geteuid()==0:
    sys.exit("\nPixie must be run as root.\n")

if not len(sys.argv) == 2:
    print "Usage:"
    print "\tpython pixie.py pixie.conf"
    os._exit(1)

import cherrypy
from lib.vm import VM
from lib.puck import Puck
from lib.jails import *
from lib.setup_plugin import SetupPlugin

from lib.controller import Controller
from controllers.configuration import ConfigurationController
from controllers.setup import SetupController

class Root(Controller):

    def __init__(self, puck):
        self._puck = puck

    @cherrypy.expose
    def index(self):
        env = dict(
            VM=self._puck.getVM()
        )
        return self.render('/index.html', **env)

cherrypy.config.update(sys.argv[1])
conf = {
    '/': {
       'request.dispatch': cherrypy.dispatch.Dispatcher()
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'static',
        'tools.staticdir.root': os.getcwd(),
        'tools.staticdir.index': 'index.html'
    }
}

puck = Puck()

root = Root(puck)
root.configure = ConfigurationController(puck)
root.setup = SetupController(puck)

daemonizer = cherrypy.process.plugins.Daemonizer(cherrpy.engine)
daemonizer.subscribe()

cherrypy.engine.vmsetup = SetupPlugin(puck, cherrypy.engine)
cherrypy.engine.vmsetup.subscribe()

cherrypy.process.plugins.SignalHandler.handlers['SIGINT'] = cherrypy.engine.exit
cherrypy.engine.signal_handler.subscribe()

app = cherrypy.tree.mount(root, '/', conf)

if hasattr(cherrypy.engine, "console_control_handler"):
    cherrypy.engine.console_control_handler.subscribe()

cherrypy.engine.start()
cherrypy.engine.block()
