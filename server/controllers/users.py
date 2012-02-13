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
from models import Users
import models

class UsersController(Controller):
    crumbs = [Crumb("/", "Home"), Crumb('/users', 'Users')]

    @cherrypy.expose
    @cherrypy.tools.myauth()
    def index(self):
        env = dict(users=Users.all())
        return self.render("/users/index.html", crumbs=self.crumbs[:-1], **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def add(self, **post):
        user = Users.new(name="", email="", username="", password="")
        meta = models.Credential.attributes
        auth_meta = dict([(k, "") for k in meta])
        auth_meta[cherrypy.config.get('virtualization.url_param')] = cherrypy.config.get('virtualization.default_url')

        if post:
            fields = ['name', 'username', 'password', 'password_repeat', 'email']
            data = self._get_data('user', fields, post)
            self._set_data(user, data)
            auth_meta = self._get_data('auth_meta', meta, post)
            user.set_meta_data(auth_meta)
            user.validate_password()

            if user.validates() and Users.add(user):
                cherrypy.session['flash'] = "Jail Type successfully added."
                raise cherrypy.HTTPRedirect("/users")

            cherrypy.session['flash'] = "Invalid data."

        env = dict(
            user = user,
            meta = meta,
            auth_meta=auth_meta
        )
        return self.render("/users/add.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def edit(self, id, **post):
        user = Users.first(id=id)
        meta = models.Credentials.attributes

        if not user:
            cherrypy.session['flash'] = "404 User Not Found"
            raise cherrypy.HTTPRedirect('/users')

        if post:
            fields = ['ip', 'netmask']
            data = self._get_data('user', fields, post)
            user.set_meta_data(self._get_data('meta', meta, post))
            if user.update(data, fields.append('virt_auth_data')):
                cherrypy.session['flash'] = "User successfully updated."
                raise cherrypy.HTTPRedirect('/users')

        env=dict(user = user, meta=meta)
        return self.render("/users/edit.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def delete(self, id):
        jail = Users.first(id=id)
        msg = "The user could not be deleted."
        if jail:
            if Users.delete(jail):
                msg = "User deleted."

        cherrypy.session['flash'] = msg

        raise cherrypy.HTTPRedirect('/users')
        attrs = ['id', 'name', 'ip']
        attrs = ['username', 'name', 'password']
        for a in attrs:
            if not a in post:
                return False
        return True


