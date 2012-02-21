import cherrypy
from pixie.lib.controller import Controller

class RootController(Controller):

    def __init__(self, lookup, puck):
        Controller.__init__(self, lookup)
        self._puck = puck

    @cherrypy.expose
    def index(self):
        env = dict(
            VM=self._puck.getVM()
        )
        return self.render('/index.html', **env)
