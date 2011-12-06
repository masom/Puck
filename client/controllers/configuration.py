import cherrypy
from lib.controller import Controller

class ConfigurationController(Controller):
    '''
    Handles configuration related controls.
    '''

    def __init__(self, lookup, puck):
        Controller.__init__(self, lookup)
        self._puck = puck
        self._vm = puck.getVM()

    def __assert_vm_is_modifiable(self):
        '''
        Checks if the VM can be modified.
        '''

        if not self._vm.status in ['new', 'configured']:
            cherrypy.session['flash'] = "The virtual machine may not be modified at this time."
            raise cherrypy.HTTPRedirect('/')

    def __assert_env_set(self):
        '''
        Checks if the VM environment has been set
        '''
        if not self._vm.environment:
            cherrypy.session['flash'] = "You must first select an environment."
            raise cherrypy.HTTPRedirect('/configure/')

    @cherrypy.expose
    def index(self):
        self.__assert_vm_is_modifiable()

        env = dict(   
            VM=self._vm,
        )

        return self.render("/configure/index.html", **env)
    @cherrypy.expose
    def environment(self, *args, **kwargs):
        self.__assert_vm_is_modifiable()

        environments = self._puck.getEnvironments()

        if cherrypy.request.method == "POST":
            if kwargs.has_key("vm.environment"): 
                env_id = kwargs['vm.environment']
                if environments.has_key(env_id):
                    self._vm.update(environment=env_id, environments=environments)
                    cherrypy.session['flash'] = "Environment updated."
                    raise cherrypy.HTTPRedirect('/configure/')

        env = dict(
            VM=self._vm,
            environments=environments
        )
        return self.render("/configure/environment.html", **env)

    @cherrypy.expose
    def jails(self, *args, **kwargs):
        self.__assert_vm_is_modifiable()
        self.__assert_env_set()

        jails = self._puck.getJails(self._vm.environment)

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
        self.__assert_vm_is_modifiable()

        keys = self._puck.getKeys()

        if cherrypy.request.method == "POST":
            if not "keys[]" in kwargs:
                raise cherrypy.HTTPRedirect('/configure/keys')

            #@todo: This should be refactored...
            #CherryPy sends a string instead of an array when there is only 1 value.
            if isinstance(kwargs['keys[]'], basestring):
                data = [kwargs['keys[]']]
            else:
                data = kwargs['keys[]']

            new_keys = dict((key, keys[key]) for key in data if key in keys)

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
        self.__assert_vm_is_modifiable()

        if not cherrypy.request.method == "POST":
            raise cherrypy.HTTPRedirect('/configure/')
        try:
            self._vm.persist()
            cherrypy.session['flash'] = "Virtual machine configuration commited."
        except IOError as e:
            cherrypy.session['flash'] = e
        raise cherrypy.HTTPRedirect('/configure/')
