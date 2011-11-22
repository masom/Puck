import cherrypy, os, sys, time, pickle

from mako.template import Template
from mako.lookup import TemplateLookup

from lib.vm import VM
from lib.puck import Puck
from lib.jails import *

class ConfigurationWizard(object):

    def __init__(self, vm):
        self._vm = vm

    def _cp_on_error(self):
        cherrypy.response.body = ("We apologise for the fault in the website. "
                                  "Those responsible have been sacked.")

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
                    vm.update(environment=environments[env_id])
                    raise cherrypy.HTTPRedirect('/configure/')

        tmpl = lookup.get_template("/configure/environment.html")
        return tmpl.render(VM=vm, environments=environments)

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

            vm.update(jails=new_jails)
            raise cherrypy.HTTPRedirect('/configure/')

        tmpl = lookup.get_template("/configure/jails.html")
        return tmpl.render(VM=vm, jails=jails)

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
            raise cherrypy.HTTPRedirect('/configure/')

        tmpl = lookup.get_template("/configure/keys.html")
        return tmpl.render(VM=vm, keys=keys)

    @cherrypy.expose
    def commit(self):
        if not cherrypy.request.method == "POST":
            raise cherrypy.HTTPRedirect('/configure/')

        if not vm.isConfigured():
            raise cherrypy.HTTPRedirect('/configure/')

        vm.persist()
        raise cherrypy.HTTPRedirect('/configure/')
        
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