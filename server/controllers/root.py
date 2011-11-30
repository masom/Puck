import cherrypy, controller, lib.vmLauncher as vmLauncher

class Root(Controller):
    plugins = [vmLauncher.Launcher]

    def __init__(self, db):
        self._db = db
        self._routes = {}
        
    @cherrypy.expose
    def index(self):
        return self.render("index.html")

    @cherrypy.expose
    def statuses(self, a=None):
        return "Nope Nope Nope"

    @cherrypy.expose
    def start(self):
        self.launcher.launch()
        cherrypy.session['flash'] = "VM started"
        raise cherrypy.HTTPRedirect("/statuses")

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

        for plugin in self.plugins:
            clsModels = dict((mcls, models[mcls]) for mcls in plugin.models)
            setattr(self, plugin.__name__.lower(), plugin(clsModels))