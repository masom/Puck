import cherrypy, controller

class Jails(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/jails", "Jails")]

    models = [models.Jail]

    def hash(self):
        return self.Jail.jails()
        
    @cherrypy.expose
    def index(self):
        env = dict(jails=self.Jail.jails())
        return self.render("jails/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    def add(self, **post):
        if post:
            self.Jail.new(post)
            cherrypy.session['flash'] = "Jail successfully added"
            raise cherrypy.HTTPRedirect("/jails")

        env = dict(
                environments=JAIL_ENVS.items(),
                jailTypes=JAIL_TYPES
        )
        return self.render("jails/add.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def view(self, jailId):
        jail = self.Jail.get(jailId)
        env = dict(jail=jail)
        return self.render("jails/view.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def delete(self, jailId):
        self.Jail.delete(jailId)

        cherrypy.session['flash'] = "Jail successfully deleted"
        raise cherrypy.HTTPRedirect("/jails")
