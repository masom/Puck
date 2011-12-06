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
import os
import cherrypy, sqlite3
from collections import namedtuple, OrderedDict
import models, controllers


templatedir = os.getcwd()
root = controllers.Root('db.sqlite3', templatedir)
root.add('jails', controllers.Jails)
root.add('keys', controllers.Keys)
root.add('api', controllers.Api)
root.add('repos', controllers.Repos)
root.load()

def connect(thread_index):
    cherrypy.thread_data.db = sqlite3.connect(root._db)

if __name__ == "__main__":
    import os
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
    cherrypy.config.update({
        'server.socket_port' : 8080,
        'server.socket_host' : '0.0.0.0'
    })

    conn = sqlite3.connect(root._db)
    models.migrate(conn, [models.Key, models.Jail, models.YumRepo])
    conn.commit()
    conn.close()
            
    cherrypy.engine.subscribe('start_thread', connect)
    cherrypy.quickstart(root, '/', conf)
