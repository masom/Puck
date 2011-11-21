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
        self.interfaces = lib.interfaces.getInterfaces()
        self._configured = False

    def persist(self):
        #TODO: pickle this into a file.
        pass

    def isConfigured(self, state = None):
        if state:
            self._configured = state
        return self._configured

class Puck(object):
    def __init__(self, vm_id = None):
        self._registration = None
        if not self.register(vm_id):
            raise LookupError()

        self._vm = VM(self._registration)

    def getVM(self):
        return self._vm

    def register(self, registration):
        '''
        TODO: USE API
        '''
        self._registration = 'ABC-DEF'
        return True

    def getJails(self):
        '''
        TODO: USE API
        '''
        jails = []
        jails.append({'type': 'content', 'url': 'http://localhost', 'name': 'Content'})
        jails.append({'type': 'database', 'url': 'http://localhost', 'name': 'Database'})
        jails.append({'type': 'support', 'url': 'http://localhost', 'name': 'Support'})
        return jails

    def updateStatus(self):
        pass

    def updateConfig(self):
        pass

    def getKeys(self):
        '''
        TODO: Use API
        '''
        keys = [
            {
                'id': 'derp',
                'name': 'Martin Samson',
                'key': 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEArsIuqG9Wictam3s6cwQdW0eedJYuoMbvF7kJ9oFprfo1UEsep30G67SPSUNwuIOIqvUwErFkiNAGjTqdnL8g7PHUInLojM3KQSGSvPgYYAZz9u9wYTy5vv2f/EphBx+FytISjoW1gL8CoiP/kX0vDLpDJnFeRQ/RbvRbiws49r/yqqf/KqXM/fwl1nhQeqwNS6K8kv3H8aaaq7cHqky0xbiDf7astFQq++jRjLIx6xX0NdU8P36IwdMFoQXdnh1B8OvMuyCxHj9y5B2wN2H/1kA0tk0dEQa1BtKNqpJF8HD2AbcTGzYczcvaCMbMV1qJe5/YTQMxjullp2cz/83Hjw=='
            }
        ]
        return keys

    def getEnvironments(self):
        '''
        TODO: Use API
        '''
        environments = {
            'dev': 'Development',
            'testing': 'Testing',
            'qa': 'Quality Assurance',
            'staging': 'Staging',
            'prod': 'Production'
        }
        return environments

class ConfigurationWizard(object):
    def __init__(self, vm):
        self._vm = vm

    @cherrypy.expose
    def index(self):
        tmpl = lookup.get_template('/configure/index.html')
        return tmpl.render(VM=vm)

    @cherrypy.expose
    def environment(self, *args, **kwargs):
        environments = puck.getEnvironments()

        if cherrypy.request.method == "POST":
            if kwargs.has_key("vm.environment"):
                env_id = kwargs['vm.environment']
                if environments.has_key(env_id):
                    vm.environment = environments[env_id]
                    print vm.environment
                    raise cherrypy.HTTPRedirect('/configure/')

        tmpl = lookup.get_template("/configure/environment.html")
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

puck = Puck()
vm = puck.getVM()

root = Root()
root.configure = ConfigurationWizard(vm)

if __name__ == "__main__":
    conf =  {'/' : 
                {
                    'request.dispatch' : cherrypy.dispatch.Dispatcher()
                }
            }
    cherrypy.quickstart(root, '/', conf)