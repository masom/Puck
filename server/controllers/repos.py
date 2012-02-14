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

class ReposController(Controller):
    crumbs = [Crumb("/", "Home"), Crumb("/repos", "Repos")]

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def index(self):
        env = dict(
            repos=YumRepositories.all(),
            environments=Environments.all()
        )
        return self.render("/repos/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def add(self, **post):
        repo = YumRepositories.new(data="", environment="")
        if post:
            fields = ['data', 'environment']
            data = self._get_data('repo', fields, post)
            self._set_data(repo, data)

            if repo.validates() and YumRepositories.add(repo):
                cherrypy.session['flash'] = "Repo successfully added"
                raise cherrypy.HTTPRedirect("/repos/index")
            cherrypy.session['flash'] = "The repository data contains errors."

        # Only list environments not having a repo.
        repos = YumRepositories.all()
        environments = Environments.all()
        envs = [env.code for env in environments]
        repos = [repo.environment for repo in repos]
        available = set(envs) - set(repos)
        return self.render("/repos/add.html", crumbs=self.crumbs, environments=environments, available=available, repo=repo)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
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
            env=Environments.first(id=repo.environment)
        )
        return self.render("/repos/edit.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def view(self, environment):
        repo = YumRepositories.first(environment=environment)
        if not repo:
            cherrypy.session['flash'] = '404 Repository Not Found'
            raise cherrypy.HTTPRedirect('/repos/index')
        env = dict(
            repo=repo,
            env=Environments.first(id=repo.environment)
        )
        return self.render("/repos/view.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def delete(self, environment):
        repo = YumRepositories.first(environment=environment)
        msg = "The user could not be deleted."
        if repo:
            if YumRepositories.delete(repo):
                msg = "Repository deleted."

        cherrypy.session['flash'] = msg

        raise cherrypy.HTTPRedirect('/repos')
