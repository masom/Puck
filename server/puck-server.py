import cherrypy
import uuid

class VM(object):
    def __init__(self):
        self._id = uuid.uuid1()
        self._config = {}
        self._status = None
        

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

class Registry(object):
    def __init__(self, cls):
        self._cls = cls
        self._container = dict()

    def new(self):
        obj = self._cls()
        self._container[obj.id()] = obj
        return obj

        
    

class Root(object):

    @cherrypy.expose
    def index(self):
        return "Hello World"

    @cherrypy.expose
    def statuses(self, a=None):
        return "Nope Nope Nope"

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

    def POST(self):
        return self._api.new().id()

class ApiStatus(ApiVmCall):

    def PUT(self):
        self._vm.status = cherrypy.request.body.read()

    def GET(self):
        return self._vm.status




class Api(object):
    def __init__(self, registry):
        self._registry = registry

    def new(self):
        vm = self._registry.new()
        setattr(self.status, vm.id(), APIStatus(self, vm))
        return name

class Stub(object):
    pass


vmRegistry = Registry(VM)
api = Api(vmRegistry)
api.registration = ApiRegistration(api)
api.status = Stub()

root = Root()
root.api = api


if __name__ == "__main__":
    conf =  {'/' : 
                {
                    'request.dispatch' : cherrypy.dispatch.Dispatcher()
                }
            ,'/api' : 
                {
                    'request.dispatch' : cherrypy.dispatch.MethodDispatcher()
                }
            }
            
    cherrypy.quickstart(root, '/', conf)
