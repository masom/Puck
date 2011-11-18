import cherrypy
import uuid

class VM(object):
    def __init__(self):
        self._id = uuid.uuid1()
        self._config = {}
        

    @property
    def id(self):
        return self._id

class Registry(object):
    def __init__(self, cls):
        self._cls = cls
        self._container = dict()

    def new(self):
        obj = self._cls()
        self._container[obj.id()] = obj
        return obj.id()

        
    

class Root(object):

    @cherrypy.expose
    def index(self):
        return "Hello World"

    @cherrypy.expose
    def statuses(self, a=None):
        return "Nope Nope Nope"

class APICall(object):
    exposed = True

    def __init__(self, registry):
        self._registry = registry


class APIRegister(APICall):

    @cherrypy.tools.json_out()
    def POST(self):
        return self._registry.new()

class APIStatus(APICall):

    @cherry



        

class Api(object):
    exposed = True

vmRegistry = Registry(VM)
api = Api()
api.register = APIRegister(vmRegistry)
api.status = APIStatus(vmRegistry)
api.keys = APIKeys(vmRegistry)
api.config = APIConfig(vmRegistry)


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
