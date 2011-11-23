import cherrypy
import uuid
from collections import namedtuple, defaultdict

from mako.template import Template
from mako.lookup   import TemplateLookup

JAIL_ENVS = {
        'dev': 'Development',
        'testing': 'Testing',
        'qa': 'Quality Assurance',
        'staging': 'Staging',
        'prod': 'Production'
    }
JAIL_TYPES = ["content", "database", "support"]


class VM(object):
    def __init__(self, ip):
        self._ip = ip
        self._id = uuid.uuid1()
        self.config = {}
        self.status = ''
        
    @property
    def id(self):
        return str(self._id).replace('-', '')

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

    @classmethod
    def render(cls, template, **variables):
        tmpl = cls.lookup.get_template(template)
        variables['flash'] = cherrypy.session.pop('flash', None)
        return tmpl.render(**variables)
    

class Root(Controller):

    @cherrypy.expose
    def index(self):
        return self.render("index.html")

    @cherrypy.expose
    def statuses(self, a=None):
        return "Nope Nope Nope"


class JailStore(object):
    Jail = namedtuple("Jail", ["name", "url", "type"])

    def __init__(self):
        self._refs = {}
        self._env = defaultdict(lambda: defaultdict(set))

    def new(self, data):
        jail = self.Jail(*tuple(data[key] for key in self.Jail._fields))
        ref = uuid.uuid1()
        self._refs[ref] = jail
        self._env[data['environment']][jail.type].add(ref)

    def jails(self):
        def sort(jails):
            return sorted(((ref, self._refs[ref]) for ref in jails),
                            key=lambda (jailId, jail) : jail.name)

        def qmap(f):
            return lambda d: dict((key, f(val)) for key, val in d.iteritems())

        return qmap(qmap(sort))(self._env)

class KeyStore(object):
    Key = namedtuple("Key", ["name", "key"])

    def __init__(self):
        self._refs = {}

    def new(self, data):
        key = self.Key(*tuple(data[key] for key in self.Key._fields))
        ref = uuid.uuid1()
        self._refs[ref] = key

    def keys(self):
        return dict(sorted(self._refs.iteritems(),
                            key=lambda (keyId, key): key.name))

    def get(self, ref):
        return self._refs[uuid.UUID(ref)]



class Jails(Controller):

    def __init__(self):
        Controller.__init__(self)

        self._store = JailStore()

    def hash(self):
        return self._store.jails()
        

    @cherrypy.expose
    def index(self):
        env = dict(jails=self._store.jails())
        return self.render("jails/index.html", **env)

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
        return self.render("jails/add.html", **env)

class Keys(Controller):
    def __init__(self):
        Controller.__init__(self)

        self._store = KeyStore()

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

root = Root()
root.jails = Jails()
root.keys = Keys()

vmRegistry = Registry(VM)
api = Api(vmRegistry)
api.registration = ApiRegistration(api, root.jails)
api.keys = ApiKeys(api, root.keys)

root.api = api



if __name__ == "__main__":
    conf =  {'/' : 
                { 'request.dispatch' : cherrypy.dispatch.Dispatcher()
                , 'tools.sessions.on' : True
                }
            ,'/api' : 
                { 'request.dispatch' : cherrypy.dispatch.MethodDispatcher()
                }
            }
            
    cherrypy.quickstart(root, '/', conf)
