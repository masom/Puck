import cherrypy
import models
from controllers.base import *

class Keys(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/keys", "Keys")]
    models = [models.Key]

    def hash(self):
        return self.Key.keys()

    @cherrypy.expose
    def index(self):
        env = dict(keys=self.Key.keys())
        return self.render("keys/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    def add(self, **post):
        if post:
            self.Key.new(post)
            cherrypy.session['flash'] = "Key successfully added"
            raise cherrypy.HTTPRedirect("/keys")
        return self.render("keys/add.html", crumbs=self.crumbs)


    @cherrypy.expose
    def view(self, keyId):
        key = self.Key.get(keyId)
        env = dict(key=key)
        return self.render("keys/view.html", crumbs=self.crumbs, **env)
