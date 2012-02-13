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
from models import Images
class ImagesController(Controller):
    crumbs = [
        Crumb("/", "Home"),
        Crumb("/images", "Virtual Images")
    ]

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def index(self):
        #Images.add(Images.new(id="test", name="test"))
        env = dict(
            images=Images.all(),
        )
        return self.render("images/index.html", self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def add(self, **post):
        image = Images.new(name="", backend_id="", description="")

        if post:
            fields = ['name', 'backend_id', 'description']
            data = self._get_data('image', fields, post)
            self._set_data(image, data)

            if image.validates() and Images.add(image):
                cherrypy.session['flash'] = "Image added"
                raise cherrypy.HTTPRedirect('/images')
            cherrypy.session['flash'] = 'Invalid data'

        backend_images = Images.get_backend_images()
        env = dict(
            image = image,
            backend_images = backend_images
        )
        return self.render("/images/add.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def edit(self, id, **post):
        image = Images.first(id=id)

        if not image:
            cherrypy.session['flash'] = "404 Image Not Found"
            raise cherrypy.HTTPRedirect('/images')

        if post:
            fields = ['name', 'backend_id', 'description']
            data = self._get_data('image', fields, post)
            if image.update(data, fields):
                cherrypy.session['flash'] = "Image successfully updated."
                raise cherrypy.HTTPRedirect('/images')

            cherrypy.session['flash'] = 'Invalid data'

        env=dict(image = image)
        return self.render("/images/edit.html", crumbs=self.crumbs, **env)

    @cherrypy.expose
    @cherrypy.tools.myauth(groups=['admin'])
    def delete(self, id):
        image = Images.first(id=id)
        msg = "The image could not be deleted."
        if image and Images.delete(image):
            msg = "Image deleted"
        cherrypy.session['flash'] = msg

        raise cherrypy.HTTPRedirect('/images')

    def _parse_backend_id(self, post):
        if post['image.backend_id'].isdigit():
            return int(post['image.backend_id'])
        else:
            return post['image.backend_id']
