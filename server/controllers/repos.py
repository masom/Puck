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
from models import YumRepositories, Environments

class Repos(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/repos", "Repos")]

    @cherrypy.expose
    def index(self):
        env = dict(
            repos=YumRepositories.all(),
            environments=Environments.all()
        )
        return self.render("/repos/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    def add(self, **post):
        if 'yum_repository' in post:
            repo = YumRepositories.new(**post)
            if repo.validates():
                YumRepositories.add(repo)
                cherrypy.session['flash'] = "Repo successfully added"
                raise cherrypy.HTTPRedirect("/repos/index")
            cherrypy.session['flash'] = "The repository data contains errors."

        # Only list environments not having a repo.
        repos = YumRepositories.all()
        environments = Environments.all()
        available = set(Environments.all().keys()) - set(repos.keys())
        return self.render("/repos/add.html", crumbs=self.crumbs, environments=environments, available=available)

    @cherrypy.expose
    def edit(self, id, **post):

        repo = YumRepositories.first(id=id)
        if not repo:
            raise cherrypy.HTTPRedirect('/repos')

        if 'repo' in post:
            if repo.validates(post['repo']):
                for k in post['repo']:
                    setattr(repo, k, post['repo'][k])
                YumRepositories.update(repo, ['data'])
                raise cherrypy.HTTPRedirect('/repos/view/%s' % id)

        env = dict(
            repo=repo,
            env=Environments.first(id=repo.environment]
        )
        return self.render("/repos/edit.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    def view(self, id):
        repo = YumRepositories.first(id=id)
        if not repo:
            cherrypy.session['flash'] = '404 Repository Not Found'
            raise cherrypy.HTTPRedirect('/repos/index')
        env = dict(
            repo=repo,
            env=Environments.first(id=repo.environment)
        )
        return self.render("/repos/view.html", crumbs=self.crumbs, **env)
