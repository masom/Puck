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
from collections import namedtuple, OrderedDict
import sqlite3

import cherrypy
from mako.template import Template
from mako.lookup   import TemplateLookup

import models

JAIL_ENVS = OrderedDict([
        ('dev','Development'),
        ('testing', 'Testing'),
        ('qa', 'Quality Assurance'),
        ('staging', 'Staging'),
        ('prod', 'Production')
        ])

JAIL_TYPES = ["content", "database", "support"]
Crumb = namedtuple("Crumb", ["url", "name"])


        
class Controller(object):
    lookup = TemplateLookup(directories=['views'])
    models = []
    sub = []

    def __init__(self, models):
        for model in self.models:
            setattr(self, model.__name__, models[model])
            

    @classmethod
    def render(cls, template, crumbs=[], **variables):
        tmpl = cls.lookup.get_template(template)
        variables['flash'] = cherrypy.session.pop('flash', None)
        variables['breadcrumbs'] = crumbs
        return tmpl.render(**variables)
    

class Root(Controller):

    def __init__(self, db):
        self._db = db
        self._routes = {}
        
    @cherrypy.expose
    def index(self):
        return self.render("index.html")

    @cherrypy.expose
    def statuses(self, a=None):
        return "Nope Nope Nope"

    def add(self, route, cls):
        self._routes[route] = cls

    def load(self):
        models = set()
        for cls in self._routes.itervalues():
            models.update(cls.models)
            models.update(*(scls.models for scls in cls.sub))

        models = dict((cls, cls({})) for cls in models)

        for route, cls in self._routes.iteritems():
            need = set(cls.models).union(*[scls.models for scls in cls.sub])
            clsModels = dict((mcls, models[mcls]) for mcls in need)
            setattr(self, route, cls(clsModels))
            



class Jails(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/jails", "Jails")]

    models = [models.Jail]

    def hash(self):
        return self.Jail.jails()
        
    @cherrypy.expose
    def index(self):
        env = dict(jails=self.Jail.jails())
        return self.render("jails/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    def add(self, **post):
        if post:
            self.Jail.new(post)
            cherrypy.session['flash'] = "Jail successfully added"
            raise cherrypy.HTTPRedirect("/jails")

        env = dict(
                environments=JAIL_ENVS.items(),
                jailTypes=JAIL_TYPES
        )
        return self.render("jails/add.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def view(self, jailId):
        jail = self.Jail.get(jailId)
        env = dict(jail=jail)
        return self.render("jails/view.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def delete(self, jailId):
        self.Jail.delete(jailId)

        cherrypy.session['flash'] = "Jail successfully deleted"
        raise cherrypy.HTTPRedirect("/jails")

class Keys(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/keys", "Keys")]
    models = [models.Key]

    def hash(self):
        return self.Key.keys()

    @cherrypy.expose
    def index(self):
        env = dict(keys=self.Key.keys())
        return self.render("keys/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    def add(self, **post):
        if post:
            self.Key.new(post)
            cherrypy.session['flash'] = "Key successfully added"
            raise cherrypy.HTTPRedirect("/keys")
        return self.render("keys/add.html", crumbs=self.crumbs)


    @cherrypy.expose
    def view(self, keyId):
        key = self.Key.get(keyId)
        env = dict(key=key)
        return self.render("keys/view.html", crumbs=self.crumbs, **env)





class ApiCall(object):
    exposed = True
    models = [models.VM]

    def __init__(self, models={}):
        for model in self.models:
            setattr(self, model.__name__, models[model])

class ApiRegistration(ApiCall):
    models = ApiCall.models + [models.Jail]

    @cherrypy.tools.json_out()
    def POST(self):
        ip = cherrypy.request.remote()
        name = self._model.register(ip)
        jails = self._jails.hash()
        return {
            'id' : name,
            'jails' : jails
        }

class ApiKeys(ApiCall):
    models = ApiCall.models + [models.Key]
    
    @cherrypy.tools.json_out()
    def GET(self):
        return self._keys.hash()

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



class Api(Controller):
    models = []
    sub = [ApiRegistration, ApiKeys, ApiStatus, ApiConfig]

    def __init__(self, models):
        Controller.__init__(self, models)

        self.registration = ApiRegistration(models)
        self.keys = ApiKeys(models)
        self.status = ApiStatus(models)
        self.config = ApiConfig(models)


root = Root('db.sqlite3')
root.add('jails', Jails)
root.add('keys', Keys)
root.add('api', Api)
root.load()

def connect(thread_index):
    cherrypy.thread_data.db = sqlite3.connect(root._db)




if __name__ == "__main__":
    import os
    conf =  {'/' : 
                { 'request.dispatch' : cherrypy.dispatch.Dispatcher()
                , 'tools.sessions.on' : True
                }
            ,'/api' : 
                { 'request.dispatch' : cherrypy.dispatch.MethodDispatcher()
                }
            , '/static' :
                { 'tools.staticdir.on': True
                , 'tools.staticdir.dir': 'static'
                , 'tools.staticdir.root': os.getcwd()
                , 'tools.staticdir.index': 'index.html'
                }
            }

    conn = sqlite3.connect(root._db)
    models.migrate(conn, [models.Key, models.Jail])
    conn.commit()
    conn.close()
            
    cherrypy.engine.subscribe('start_thread', connect)
    cherrypy.quickstart(root, '/', conf)
