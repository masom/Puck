import cherrypy, sqlite3
from collections import namedtuple, OrderedDict
import models, controllers

JAIL_ENVS = OrderedDict([
        ('dev','Development'),
        ('testing', 'Testing'),
        ('qa', 'Quality Assurance'),
        ('staging', 'Staging'),
        ('prod', 'Production')
        ])

JAIL_TYPES = ["content", "database", "support"]
Crumb = namedtuple("Crumb", ["url", "name"])

root = controllers.Root('db.sqlite3')
root.add('jails', controllers.Jails)
root.add('keys', controllers.Keys)
root.add('api', controllers.Api)
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

    conn = sqlite3.connect(root._db)
    models.migrate(conn, [models.Key, models.Jail])
    conn.commit()
    conn.close()

    cherrypy.engine.subscribe('start_thread', connect)
    cherrypy.quickstart(root, '/', conf)
