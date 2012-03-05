#!/usr/local/bin/python27
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
import os, sys, time, json

import cherrypy
from mako.lookup import TemplateLookup

import pixie
from pixie.lib.vm import VM
from pixie.lib.puck import Puck
from pixie.lib.jails import EzJailStarter
from pixie.lib.setup_plugin import SetupPlugin

from pixie.lib.controller import Controller
from pixie.controllers.root import RootController
from pixie.controllers.configuration import ConfigurationController
from pixie.controllers.setup import SetupController

import socket

CONF = {
    '/': {
       'request.dispatch': cherrypy.dispatch.Dispatcher()
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'static',
        'tools.staticdir.root': os.path.dirname(pixie.__file__),
        'tools.staticdir.index': 'index.html'
    }
}

def argparser():
    import argparse

    parser = argparse.ArgumentParser(description="Puck client")
    parser.add_argument("-c", "--config", default="/etc/pixie.conf")
    parser.add_argument("-d", "--daemonize", action="store_true")
    parser.add_argument("-t", "--templatedir", default=os.path.dirname(pixie.__file__))
    return parser

def start_jail_launcher():
    ''' Workaround for threads breaking ezjail-admin start '''
    launcher = EzJailStarter()
    socket_file = launcher.getSocketFile()
    if os.path.exists(socket_file):
        os.unlink(socket_file)

    pid = os.fork()
    if pid == 0:
        # Child here
        launcher.run()
        cherrypy.log("Child process exiting.")
        os._exit(0)

    cherrypy.log("Child process is %s. Awaiting available socket." % pid)
    attempts = 0
    while not os.path.exists(socket_file):
        time.sleep(0.1)
        attempts += 1
        if (attempts > 50):
            cherrypy.log("Child process is not listening on socket!")
            os._exit(1)

    ezjc_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    ezjc_socket.connect(socket_file)
    return (pid, ezjc_socket)

if __name__ == "__main__":

    if not sys.version_info >= (2,7):
        sys.exit("Python 2.7 is required for Pixie.")

    if not os.geteuid()==0:
        sys.exit("\nPixie must be run as root.\n")

    parser = argparser()
    args = parser.parse_args()

    (pid, ezjl_socket) = start_jail_launcher()

    if args.daemonize:
        daemonizer = cherrypy.process.plugins.Daemonizer(cherrypy.engine)
        daemonizer.subscribe()


    cherrypy.config.update(args.config)

    lookup = TemplateLookup(
        directories=[os.path.join(args.templatedir, reldir) for reldir in ["html"]]
    )

    puck = Puck()
    puck.getVM().jails.setSocket(ezjl_socket)

    root = RootController(lookup, puck)
    root.configure = ConfigurationController(lookup, puck)
    root.setup = SetupController(lookup, puck)

    cherrypy.engine.vmsetup = SetupPlugin(puck, cherrypy.engine)
    cherrypy.engine.vmsetup.subscribe()

    cherrypy.process.plugins.SignalHandler.handlers['SIGINT'] = cherrypy.engine.exit
    cherrypy.engine.signal_handler.subscribe()

    if hasattr(cherrypy.engine, "console_control_handler"):
        cherrypy.engine.console_control_handler.subscribe()

    app = cherrypy.tree.mount(root, '/', CONF)

    cherrypy.engine.start()
    cherrypy.engine.block()
    try:
        ezjl_socket.sendall(json.dumps({'id': 'shutdown'}))
        ezjl_socket.close()
    except:
        cherrypy.log("Could not send shutdown command to child.")
    # Wait for the child to terminate.
    os.waitpid(pid, 0)
