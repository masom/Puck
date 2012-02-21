import cherrypy
from pixie.lib.controller import Controller

class SetupController(Controller):
    '''
    Handles setup-related controls.
    '''

    def __init__(self, lookup, puck):
        Controller.__init__(self, lookup)
        self._puck = puck
        self._vm = puck.getVM()

    def __canSetup(self):
        '''
        Checks if the virtual machine can run the setup.
        If it cannot, the user is redirected to the app index.
        '''

        if not self._vm.status in ['configured', 'setup', 'setup_failed'] or not self._vm.isConfigured():
            cherrypy.session['flash'] = "The virtual machine may not be setup at this time."
            raise cherrypy.HTTPRedirect('/')

        if self._vm.status == 'configured':
            self._vm.status = 'setup'
            self._puck.updateConfig()
            self._vm.persist()

    @cherrypy.expose
    def index(self):
        self.__canSetup()
        raise cherrypy.HTTPRedirect('/setup/start')

    @cherrypy.expose
    def start(self):
        self.__canSetup()

        cherrypy.engine.publish("setup", action="start")
        raise cherrypy.HTTPRedirect('/setup/status')

    @cherrypy.expose
    def status(self):
        (statuses, running) = cherrypy.engine.publish("setup", action="status").pop()
        env = dict(
            VM = self._vm,
            statuses = statuses,
            setup_running = running
        )
        return self.render("/setup/status.html", **env)
    @cherrypy.expose
    def status_clear(self):
        cherrypy.engine.publish("setup", action="clear")
        raise cherrypy.HTTPRedirect('/setup/status')
