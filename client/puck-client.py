import cherrypy, os, sys, time, pickle
import lib.interfaces

from mako.template import Template
from mako.lookup import TemplateLookup

class VM(object):
    def __init__(self, id = None):
        self.id = id
        self.jails = []
        self.keys = {}
        self.status = None
        self.environment = None
        self.interfaces = lib.interfaces.getInterfaces();
        self._configured = False

    def persist(self):
        #TODO: pickle this into a file.
        pass

    def isConfigured(self, state = None):
        if state:
            self._configured = state
        return self._configured
        
class Puck(object):
    def __init__(self, vm):
        self._vm = vm

    def register(self):
        pass

    def updateStatus(self):
        pass

    def updateConfig(self):
        pass

    def getKeys(self):
        pass
    def getEnvironments(self):
        return {
            'dev': 'Development',
            'testing': 'Testing',
            'qa': 'Quality Assurance',
            'staging': 'Staging',
            'prod': 'Production'
        }

class ConfigurationWizard(object):
    def __init__(self, vm):
        self._vm = vm

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('/configure/environment', status=303)

    @cherrypy.expose
    def environment(self, *args,**kwargs):
        if cherrypy.request.method == "POST":
            if kwargs.has_key("vm.environment"):
                vm.environment = kwargs['vm.environment']

        environments = puck.getEnvironments()

        tmpl = lookup.get_template("configure/environment.html")
        return tmpl.render(VM=vm, environments=environments)

    @cherrypy.expose
    def jails(self):
        return "Nope Nope Nope"

    @cherrypy.expose
    def keys(self):
        return "HAHAHA"

    @cherrypy.expose
    def save(self):
        return "saved"

class Root(object):

    @cherrypy.expose
    def index(self):
        tmpl = lookup.get_template("index.html")
        return tmpl.render(VM=vm)

lookup = TemplateLookup(directories=['html'])

vm = VM()
puck = Puck(vm)

root = Root()
root.configure = ConfigurationWizard(vm)

if __name__ == "__main__":
    conf =  {'/' : 
                {
                    'request.dispatch' : cherrypy.dispatch.Dispatcher()
                }
            }
    cherrypy.quickstart(root, '/', conf)