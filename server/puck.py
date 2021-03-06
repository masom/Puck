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
import os, sys
import cherrypy, sqlite3
from mako.lookup import TemplateLookup
from plugins.virtualization import VirtualizationPlugin

def argparser():
    import argparse

    parser = argparse.ArgumentParser(description="Puck")
    parser.add_argument("-c", "--config", default="/etc/puck.conf")
    parser.add_argument("-d", "--daemonize", action="store_true")
    parser.add_argument("-t", "--templatedir", default=os.getcwd())
    parser.add_argument("-i", "--init", action="store_true")
    return parser

def connect(thread_index):
    cherrypy.thread_data.db = sqlite3.connect(cherrypy.config.get('database.file'))
    cherrypy.thread_data.db.row_factory = sqlite3.Row

if __name__ == "__main__":

    if not sys.version_info >= (2,7):
        sys.exit("Python 2.7 is required for Puck.")

    parser = argparser()
    args = parser.parse_args()

    if args.daemonize:
        daemonizer = cherrypy.process.plugins.Daemonizer(cherrypy.engine)
        daemonizer.subscribe()

    cherrypy.config.update(args.config)

    lookup = TemplateLookup(
        directories=[os.path.join(args.templatedir, reldir) for reldir in ["views"]]
    )

    conf =  {
        '/' : {
            'request.dispatch' : cherrypy.dispatch.Dispatcher(),
            'tools.sessions.on' : True
        },
        '/api' : {
            'request.dispatch' : cherrypy.dispatch.MethodDispatcher()
        },
        '/static' : {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static',
            'tools.staticdir.root': os.getcwd(),
            'tools.staticdir.index': 'index.html'
        }
    }

    connect(None)

    import libs.controller
    cherrypy.tools.myauth = cherrypy.Tool("before_handler", libs.controller.auth)

    import models, controllers
    if args.init:
        cherrypy.log("Initializing persistent storage.")
        from libs.model import Migration
        m = Migration(cherrypy.thread_data.db, [])
        m.init()

        models.Users.load()
        if models.Users.first(username='admin'):
            cherrypy.log('Admin account already created, skipping.')
            os._exit(0)

        user = models.Users.new(username='admin', user_group='admin', name='Administrator')
        user.password = models.Users.hash_password('puck')
        if models.Users.add(user):
            cherrypy.log('Admin account added.')
            cherrypy.log('\tUsername: admin')
            cherrypy.log('\tPassword: puck')
            os._exit(0)
        else:
            cherrypy.log('An error occured while creating the admin account.')
            os._exit(1)

    cherrypy.log("Loading models from persistent storage.")
    models.load()

    cherrypy.log("Loading virtualization plugin.")
    cherrypy.engine.virtualization = VirtualizationPlugin(cherrypy.engine)
    cherrypy.engine.virtualization.subscribe()
    models.Credential = cherrypy.engine.virtualization.get_credential_class()

    cherrypy.log("Loading controllers.")
    root = controllers.RootController(lookup)
    root.add('api', controllers.Api)
    root.add('environments', controllers.EnvironmentsController)
    root.add('firewalls', controllers.FirewallsController)
    root.add('images', controllers.ImagesController)
    root.add('jail_types', controllers.JailTypesController)
    root.add('jails', controllers.JailsController)
    root.add('keys', controllers.KeysController)
    root.add('repos', controllers.ReposController)
    root.add('users', controllers.UsersController)
    root.add('virtual_machines', controllers.VirtualMachinesController)
    root.load()

    cherrypy.log("Starting application.")
    cherrypy.engine.subscribe('start_thread', connect)
    cherrypy.quickstart(root, '/', conf)
