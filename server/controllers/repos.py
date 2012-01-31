'''
Puck: FreeBSD virtualization guest configuration server
Copyright (C) 2011  The Hotel Communication Network inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import cherrypy
from libs.controller import *

class Repos(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/repos", "Repos")]

    @cherrypy.expose
    def index(self):
        env = dict(
            repos=self.YumRepo.repos(),
            environments=self.Environment.get()
        )
        return self.render("/repos/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    def add(self, **post):
        if post:
            try:
                self.YumRepo.create(post)
                cherrypy.session['flash'] = "Repo successfully added"
                raise cherrypy.HTTPRedirect("/repos/index")
            except KeyError as e:
                cherrypy.session['flash'] = "There was a problem adding the new repository: %s" % e

        # Only list environments not having a repo.
        repos = self.YumRepo.repos()
        environments = self.Environment.get()
        available = set(self.Environment.get().keys()) - set(repos.keys())
        return self.render("/repos/add.html", crumbs=self.crumbs, environments=environments, available=available)

    @cherrypy.expose
    def edit(self, id, **post):

        repo = self.YumRepo.get(id)
        if not repo:
            raise cherrypy.HTTPRedirect('/repos')

        if post:
            self.YumRepo.update(post)
            raise cherrypy.HTTPRedirect('/repos/view/%s' % id)

        env = dict(
            repo=repo,
            env=self.Environment.get()[repo.environment]
        )
        return self.render("/repos/edit.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def view(self, id):
        env = dict(
            repo=self.YumRepo.get(id),
            env=self.Environment.get()[id]
        )
        return self.render("/repos/view.html", crumbs=self.crumbs, **env)
