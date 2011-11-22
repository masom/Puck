import cherrypy
import uuid

from mako.template import Template
from mako.lookup   import TemplateLookup

JAIL_ENVS = ["Dev", "Staging", "QA"]
JAIL_TYPES = ["content", "whatever", "essential"]

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
        return tmpl.render(**variables)
    

class Root(Controller):

    @cherrypy.expose
    def index(self):
        return self.render("index.html")

    @cherrypy.expose
    def statuses(self, a=None):
        return "Nope Nope Nope"

class Jails(Controller):
    @cherrypy.expose
    def index(self):
        jails = []
        env = dict(   
            jails=[],
            flash = cherrypy.session.pop('flash', None),
        )
        return self.render("jails/index.html", **env)

    @cherrypy.expose
    def add(self, **post):
        if post:
            cherrypy.session['flash'] = "Jail successfully added"
            raise cherrypy.HTTPRedirect("/jails")

        env = dict(
                environments=JAIL_ENVS,
                jailTypes=JAIL_TYPES
        )
        return self.render("jails/add.html", **env)


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

    @cherrypy.tools.json_out()
    def POST(self):
        ip = cherrypy.request.remote()
        name = self._api.new(ip)
        jails = []
        return {
            'id' : name,
            'jails' : jails
        }

class ApiKeys(ApiCall):
    
    @cherrypy.tools.json_out()
    def GET(self):
        return {}

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


vmRegistry = Registry(VM)
api = Api(vmRegistry)
api.registration = ApiRegistration(api)

root = Root()
root.api = api
root.jails = Jails()


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
