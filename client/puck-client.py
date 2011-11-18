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
    def persist(self):
        #TODO: pickle this into a file.
        pass

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

class Configuration(object):
    def __init__(self, vm):
        self._vm = vm

    @cherrypy.expose
    def index(self):
        return "index"

    @cherrypy.expose
    def environment(self):
        return "Nope Nope Nope"

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
root.configure = Configuration(vm)

if __name__ == "__main__":
    conf =  {'/' : 
                {
                    'request.dispatch' : cherrypy.dispatch.Dispatcher()
                }
            }
    cherrypy.quickstart(root, '/', conf)