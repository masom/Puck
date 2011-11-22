import cherrypy, os, sys, time, pickle

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

class ConfigurationWizard(Controller):

    def __init__(self, vm):
        self._vm = vm

    @cherrypy.expose
    def index(self):

        env = dict(   
            VM=vm,
        )

        return self.render("/configure/index.html", **env)
    @cherrypy.expose
    def environment(self, *args, **kwargs):
        environments = puck.getEnvironments()

        if cherrypy.request.method == "POST":
            if kwargs.has_key("vm.environment"): 
                env_id = kwargs['vm.environment']
                if environments.has_key(env_id):
                    vm.update(environment=environments[env_id])
                    cherrypy.session['flash'] = "Environment updated."
                    raise cherrypy.HTTPRedirect('/configure/')

        env = dict(
            VM=vm,
            environments=environments
        )
        return self.render("/configure/environment.html", **env)

    @cherrypy.expose
    def jails(self, *args, **kwargs):
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
            vm.update(jails=new_jails)
            raise cherrypy.HTTPRedirect('/configure/')

        env = dict(
            VM=vm,
            jails=jails,
        )
        return self.render("/configure/jails.html", **env)

    @cherrypy.expose
    def keys(self, *args, **kwargs):
        keys = puck.getKeys()

        if cherrypy.request.method == "POST":
            if not "keys[]" in kwargs:
                raise cherrypy.HTTPRedirect('/configure/keys')

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

            vm.update(keys=new_keys)
            cherrypy.session['flash'] = "Authentication keys updated."
            raise cherrypy.HTTPRedirect('/configure/')

        env = dict(
            VM=vm,
            keys=keys,
        )
        return self.render("/configure/keys.html", **env)

    @cherrypy.expose
    def save(self):
        if not cherrypy.request.method == "POST":
            raise cherrypy.HTTPRedirect('/configure/')
        try:
            vm.persist()
            cherrypy.session['flash'] = "Virtual machine configuration commited."
        except IOError as e:
            cherrypy.session['flash'] = e
        raise cherrypy.HTTPRedirect('/configure/')

class Root(Controller):

    @cherrypy.expose
    def index(self):
        env = dict(
            VM=vm
        )
        return self.render('/index.html', **env)

puck = Puck()
vm = puck.getVM()

root = Root()
root.configure = ConfigurationWizard(vm)

if __name__ == "__main__":
    conf =  {'/' : 
                {
                    'request.dispatch' : cherrypy.dispatch.Dispatcher(),
                    'tools.sessions.on' : True
                }
            }
    cherrypy.quickstart(root, '/', conf)