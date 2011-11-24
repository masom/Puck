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



class Registry(object):
    def __init__(self, cls):
        self._cls = cls
        self._container = dict()

    def new(self, *args):
        obj = self._cls(*args)
        self._container[obj.id] = obj
        return obj

        
class Controller(object):
    lookup = TemplateLookup(directories=['views'])

    def __init__(self, store):
        self._store = store

    @classmethod
    def render(cls, template, crumbs=[], **variables):
        tmpl = cls.lookup.get_template(template)
        variables['flash'] = cherrypy.session.pop('flash', None)
        variables['breadcrumbs'] = crumbs
        return tmpl.render(**variables)
    

class Root(Controller):

    def __init__(self, db):
        self._db = db
        
    @cherrypy.expose
    def index(self):
        return self.render("index.html")

    @cherrypy.expose
    def statuses(self, a=None):
        return "Nope Nope Nope"

    def add(self, route, cls):

        store = cls.Store()
        setattr(self, route, cls(store))


class Jails(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/jails", "Jails")]

    Store = models.Jail

    def hash(self):
        return self._store.jails()
        
    @cherrypy.expose
    def index(self):
        env = dict(jails=self._store.jails())
        return self.render("jails/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    def add(self, **post):
        if post:
            self._store.new(post)
            cherrypy.session['flash'] = "Jail successfully added"
            raise cherrypy.HTTPRedirect("/jails")

        env = dict(
                environments=JAIL_ENVS.items(),
                jailTypes=JAIL_TYPES
        )
        return self.render("jails/add.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def view(self, jailId):
        jail = self._store.get(jailId)
        env = dict(jail=jail)
        return self.render("jails/view.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def delete(self, jailId):
        self._store.delete(jailId)

        cherrypy.session['flash'] = "Jail successfully deleted"
        raise cherrypy.HTTPRedirect("/jails")

class Keys(Controller):
    Store = models.Key

    def hash(self):
        return self._store.keys()

    @cherrypy.expose
    def index(self):
        env = dict(keys=self._store.keys())
        return self.render("keys/index.html", **env)

    @cherrypy.expose
    def add(self, **post):
        if post:
            self._store.new(post)
            cherrypy.session['flash'] = "Key successfully added"
            raise cherrypy.HTTPRedirect("/keys")
        return self.render("keys/add.html")


    @cherrypy.expose
    def view(self, keyId):
        key = self._store.get(keyId)
        env = dict(key=key)
        return self.render("keys/view.html", **env)





class ApiCall(object):
    exposed = True

    def __init__(self, api):
        self._api = api

class ApiVmCall(object):
    exposed = True

    def __init__(self, api, vm):
        self._vm = vm
        self._api = api


class ApiRegistration(ApiCall):
    def __init__(self, api, jails):
        ApiCall.__init__(self, api)
        self._jails = jails

    @cherrypy.tools.json_out()
    def POST(self):
        ip = cherrypy.request.remote()
        name = self._api.new(ip)
        jails = self._jails.hash()
        return {
            'id' : name,
            'jails' : jails
        }

class ApiKeys(ApiCall):
    def __init__(self, api, keys):
        ApiCall.__init__(self, api)
        self._keys = keys
        
    
    @cherrypy.tools.json_out()
    def GET(self):
        return self._keys.hash()

class ApiStatus(ApiVmCall):

    def PUT(self):
        self._vm.status = cherrypy.request.body.read()

    def GET(self):
        return self._vm.status

class ApiConfig(ApiVmCall):

    @cherrypy.tools.json_in()
    def POST(self):
        print(cherrypy.request.json)
        print(cherrypy.request.remote)

    @cherrypy.tools.json_out()
    def GET(self):
        return self._vm.config



class Api(object):
    def __init__(self, registry):
        self._registry = registry

        self.status = Stub()
        self.config = Stub()

    def new(self):
        vm = self._registry.new()
        setattr(self.status, vm.id, ApiStatus(self, vm))
        setattr(self.config, vm.id, ApiConfig(self, vm))
        return vm.id

class Stub(object):
    pass


root = Root('db.sqlite3')
root.add('jails', Jails)
root.add('keys', Keys)

vmRegistry = Registry(models.VM)
api = Api(vmRegistry)
api.registration = ApiRegistration(api, root.jails)
api.keys = ApiKeys(api, root.keys)

root.api = api

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
