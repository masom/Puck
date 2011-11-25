import cherrypy, os, sys, time, pickle, threading, Queue as queue

from cherrypy.process import wspbus, plugins

from mako.template import Template
from mako.lookup import TemplateLookup

from lib.vm import VM
from lib.puck import Puck
from lib.jails import *

class Controller(object):
    def _cp_on_error(self):
        cherrypy.response.body = ("We apologise for the fault in the website. "
                                  "Those responsible have been sacked.")

    lookup = TemplateLookup(directories=['html'])

    @classmethod
    def render(cls, template, **variables):
        variables['flash'] = cherrypy.session.pop('flash', None)
        tmpl = cls.lookup.get_template(template)
        return tmpl.render(**variables)

class VMController(Controller):
    def __init__(self, vm):
        self._vm = vm

    def __canSetup(self):
        if not self._vm.status in ['configured', 'setup'] or not self._vm.isConfigured():
            cherrypy.session['flash'] = "The virtual machine may not be setup at this time."
            raise cherrypy.HTTPRedirect('/')
        
        if self._vm.status == 'configured':
            self._vm.status = 'setup'
            self._vm.persist()

    @cherrypy.expose
    def setup(self):
        self.__canSetup()

        cherrypy.bus.publish('setup-start')

        raise cherrypy.HTTPRedirect('/status')
        
    
class ConfigurationController(Controller):

    def __init__(self, vm):
        self._vm = vm

    def __canVMBeModified(self):
        if not self._vm.status in ['new', 'configured']:
            cherrypy.session['flash'] = "The virtual machine may not be modified at this time."
            raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def index(self):
        self.__canVMBeModified()

        env = dict(   
            VM=self._vm,
        )

        return self.render("/configure/index.html", **env)
    @cherrypy.expose
    def environment(self, *args, **kwargs):
        self.__canVMBeModified()

        environments = puck.getEnvironments()

        if cherrypy.request.method == "POST":
            if kwargs.has_key("vm.environment"): 
                env_id = kwargs['vm.environment']
                if environments.has_key(env_id):
                    self._vm.update(environment=environments[env_id])
                    cherrypy.session['flash'] = "Environment updated."
                    raise cherrypy.HTTPRedirect('/configure/')

        env = dict(
            VM=self._vm,
            environments=environments
        )
        return self.render("/configure/environment.html", **env)

    @cherrypy.expose
    def jails(self, *args, **kwargs):
        self.__canVMBeModified()

        jails = puck.getJails()

        if cherrypy.request.method == "POST":
            #@todo: Move this somewhere else
            keys = ['jails.content', 'jails.database', 'jails.support']

            new_jails = []

            for key in kwargs:
                if not key in keys:
                    continue

                jail_id = kwargs[key]
                domain, type = key.split('.', 1)
                if jails[type].has_key(jail_id):
                    new_jails.append(jails[type][jail_id])

            cherrypy.session['flash'] = "Jails configuration updated."
            self._vm.update(jails=new_jails)
            raise cherrypy.HTTPRedirect('/configure/')

        env = dict(
            VM=self._vm,
            jails=jails,
        )
        return self.render("/configure/jails.html", **env)

    @cherrypy.expose
    def keys(self, *args, **kwargs):
        self.__canVMBeModified()

        keys = puck.getKeys()

        if cherrypy.request.method == "POST":
            if not "keys[]" in kwargs:
                raise cherrypy.HTTPRedirect('/conself.__canVMBeModified()figure/keys')

            #@todo: This should be refactored...
            #CherryPy sends a string instead of an array when there is only 1 value.
            if isinstance(kwargs['keys[]'], basestring):
                data = [kwargs['keys[]']]
            else:
                data = kwargs['keys[]']

            new_keys = {}
            for key in data:
                if not key in keys:
                    continue
                new_keys[key]= keys[key]

            self._vm.update(keys=new_keys)
            cherrypy.session['flash'] = "Authentication keys updated."
            raise cherrypy.HTTPRedirect('/configure/')

        env = dict(
            VM=self._vm,
            keys=keys,
        )
        return self.render("/configure/keys.html", **env)

    @cherrypy.expose
    def save(self):
        self.__canVMBeModified()

        if not cherrypy.request.method == "POST":
            raise cherrypy.HTTPRedirect('/configure/')
        try:
            self._vm.persist()
            cherrypy.session['flash'] = "Virtual machine configuration commited."
        except IOError as e:
            cherrypy.session['flash'] = e
        raise cherrypy.HTTPRedirect('/configure/')

class Root(Controller):

    def __init__(self, vm):
        self._vm = vm

    @cherrypy.expose
    def index(self):
        env = dict(
            VM=self._vm
        )
        return self.render('/index.html', **env)

class SetupPlugin(plugins.SimplePlugin):
    class SetupWorkerThread(threading.Thread):
        """Thread class with a stop() method. The thread itself has to check
        regularly for the stopped() condition."""
    
        def __init__(self, bus=None, queue=None):
            super(SetupWorkerThread, self).__init__()
            self._stop = threading.Event()
    
        def stop(self):
            self._stop.set()
    
        def stopped(self):
            return self._stop.isSet()

    def __init__(self, bus, freq=30.0):
        plugins.SimplePlugin.__init__(self, bus)
        self.freq = freq
        self._queue = queue.Queue()
        self.worker = threading.Thread(name="SetupWorkerThread", target=self.SetupWorkerThread, kwargs={'bus': bus, 'queue': self._queue})

    def start(self):
        self.bus.log('Starting up setup tasks')
        self.bus.subscribe('setup-start', self.switch)
        self.bus.subscribe('setup-status', self.switch)
        self.bus.subscribe('setup-stop', self.switch)
    start.priority = 70

    def stop(self):
        self.bus.log('Stopping down setup task.')
        self._setup_stop();

    def switch(self, *args, **kwargs):
        self.bus.log("Switch called. Linking call.")
        if not 'action' in kwargs:
            return

        def default(**kwargs):
            return

        {
         'start': self._setup_start,
         'stop': self._setup_stop,
         'status': self._setup_status
        }.get(kwargs['action'], default)()

    def _setup_stop(self, **kwargs):
        self.bus.log("Stop called. Giving back time.")
        if self.worker.isAlive():
            self.worker.stop()

    def _setup_start(self, **kwargs):
        self.bus.log("Start called. Starting time.")
        if not self.worker.isAlive():
            self.worker.start()

    def _setup_status(self, **kwargs):
        self.bus.log('Status called. Wants its time back.')

puck = Puck()
vm = puck.getVM()

root = Root(vm)
root.configure = ConfigurationController(vm)
root.vm = VMController(vm)

if __name__ == "__main__":
    conf =  {'/' : 
                {
                    'request.dispatch' : cherrypy.dispatch.Dispatcher(),
                    'tools.sessions.on' : True
                }
            }

    cherrypy.engine.vmsetup = SetupPlugin(cherrypy.engine)
    cherrypy.engine.vmsetup.subscribe()

    cherrypy.quickstart(root, '/', conf)