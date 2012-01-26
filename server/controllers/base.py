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

Crumb = namedtuple("Crumb", ["url", "name"])

class Controller(object):
    models = []
    sub = []

    def __init__(self, lookup, models):
        self._lookup = lookup

        for model in self.models:
            setattr(self, model.__name__, models[model])

    def render(self, template, crumbs=[], **variables):
        tmpl = self._lookup.get_template(template)
        variables['flash'] = cherrypy.session.pop('flash', None)
        variables['breadcrumbs'] = crumbs
        return tmpl.render(**variables)

    def load(self):
        models = set(self.models)
        for cls in self._routes.itervalues():
            models.update(cls.models)
            models.update(*(scls.models for scls in cls.sub))

        models = dict((cls, cls({})) for cls in models)

        for route, cls in self._routes.iteritems():
            need = set(cls.models).union(*[scls.models for scls in cls.sub])
            clsModels = dict((mcls, models[mcls]) for mcls in need)
            setattr(self, route, cls(self._lookup, clsModels))

        for model in self.models:
            etattr(self, model.__name__, models[model])
