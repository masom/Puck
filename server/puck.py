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
import models, controllers

from plugins.virtualization import VirtualizationPlugin

def argparser():
    import argparse

    parser = argparse.ArgumentParser(description="Puck")
    parser.add_argument("-c", "--config", default="/etc/puck.conf")
    parser.add_argument("-d", "--daemonize", action="store_true")
    parser.add_argument("-t", "--templatedir", default=os.getcwd())
    return parser

def connect(thread_index):
    cherrypy.thread_data.db = sqlite3.connect(root._db)
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

    cherrypy.engine.virtualization = VirtualizationPlugin(cherrypy.engine)
    cherrypy.engine.virtualization.subscribe()

    root = controllers.Root(cherrypy.config.get('database.file'), lookup)
    root.add('jails', controllers.Jails)
    root.add('keys', controllers.Keys)
    root.add('api', controllers.Api)
    root.add('repos', controllers.Repos)
    root.add('virtual_machines', controllers.VirtualMachines)
    root.load()

    conn = sqlite3.connect(root._db)
    models.migrate(conn, [models.Key, models.Jail, models.VM, models.YumRepo, models.Image])
    conn.commit()
    conn.close()

    cherrypy.engine.subscribe('start_thread', connect)
    cherrypy.quickstart(root, '/', conf)
