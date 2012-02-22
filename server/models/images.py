'''
Puck: FreeBSD virtualization guest configuration server
Copyright (C) 2012  The Hotel Communication Network inc.

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

from libs.model import ModelCollection, Model, TableDefinition
from collections import OrderedDict
import cherrypy

class Image(Model):
    def __init__(self, id=None, name="", backend_id=None, description=""):
        self.id = id
        self.name = name
        self.backend_id = backend_id
        self.description = description

    def validates(self):
        backend_ids = [i.id for i in self._collection.get_backend_images()]
        if not self.backend_id in backend_ids:
            return False
        return True

class Images(ModelCollection):
    _model = Image

    def _generate_table_definition(self):
        columns = OrderedDict([
            ('id', "TEXT"),
            ('name', "TEXT"),
            ('backend_id', 'TEXT'),
            ('description', 'TEXT')
        ])
        return TableDefinition('images', columns=columns)

    def get_backend_images(self):
        cherrypy.session['credentials'] = cherrypy.session.get('credentials')
        args = dict(
            action = "images",
            credentials=cherrypy.session.get('credentials')
        )
        return cherrypy.engine.publish("virtualization", **args).pop()
