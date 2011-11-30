import cherrypy
from controllers.base import *
import models

def asdict(jailId, jail):
    return dict(zip(jail._fields + ("id",), jail + (jailId,)))

class ApiCall(object):
    exposed = True
    models = []

    def __init__(self, models={}):
        for model in self.models:
            setattr(self, model.__name__, models[model])

class ApiRegistration(ApiCall):
    models = [models.VM]

    @cherrypy.tools.json_out()
    def POST(self):
        name = self.VM.register(cherrypy.request.remote.ip)
        return {
            'id' : name,
        }

class ApiKeys(ApiCall):
    models = [models.Key]
    
    @cherrypy.tools.json_out()
    def GET(self):
        keys = self.Key.keys()

        return dict((keyId, asdict(keyId, key)) for keyId, key in keys)


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

class ApiEnvironments(ApiCall):
    models = [models.Environment]

    @cherrypy.tools.json_out()
    def GET(self):
        return self.Environment.get()

class ApiJails(ApiCall):
    exposed = True
    models = [models.Jail]

    @cherrypy.tools.json_out()
    def GET(self, environment=None):
        jails = self.Jail.jails()[environment]

        result = dict()
        for typ, typJails in jails.iteritems():
            result[typ] = dict((jailId, asdict(jailId, jail))
                                    for jailId, jail in typJails)
        return result


class Api(Controller):
    models = []
    sub = [ApiRegistration, ApiKeys, ApiStatus, ApiConfig,
           ApiEnvironments, ApiJails]

    def __init__(self, models):
        Controller.__init__(self, models)

        self.registration = ApiRegistration(models)
        self.keys = ApiKeys(models)
        self.status = ApiStatus(models)
        self.config = ApiConfig(models)
        self.environments = ApiEnvironments(models)
        self.jails = ApiJails(models)
