import cherrypy, controller

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