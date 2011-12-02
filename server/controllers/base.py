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
from collections import namedtuple

import cherrypy

from mako.template import Template
from mako.lookup   import TemplateLookup


Crumb = namedtuple("Crumb", ["url", "name"])

class Controller(object):
    lookup = TemplateLookup(directories=['views'])
    models = []
    sub = []

    def __init__(self, models):
        for model in self.models:
            setattr(self, model.__name__, models[model])
            
    @classmethod
    def render(cls, template, crumbs=[], **variables):
        tmpl = cls.lookup.get_template(template)
        variables['flash'] = cherrypy.session.pop('flash', None)
        variables['breadcrumbs'] = crumbs
        return tmpl.render(**variables)
