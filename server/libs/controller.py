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
import functools
import cherrypy

Crumb = namedtuple("Crumb", ["url", "name"])

class Controller(object):

    def __init__(self, lookup):
        self._lookup = lookup

    def _set_data(self, entity, data):
        for k in data:
            setattr(entity, k, data[k])

    def _get_data(self, prefix, fields, post):
        data = dict((k.split(".", 1)[1], post[k]) for k in post if k.startswith('%s.' % prefix))
        return dict((k, data[k]) for k in data if k in fields)

    def render(self, template, crumbs=[], **variables):
        tmpl = self._lookup.get_template(template)
        variables['flash'] = cherrypy.session.pop('flash', None)
        variables['breadcrumbs'] = crumbs
        return tmpl.render(**variables)

def auth(groups=[]):
    # http://stackoverflow.com/questions/3302844/writing-a-cherrypy-decorator-for-authorization
    if not cherrypy.session.has_key('user.id'):
        raise cherrypy.HTTPRedirect('/login')

    if not groups:
        return

    if not cherrypy.session.get('user.group', None) in groups:
        cherrypy.session['flash'] = 'You are not authorized to access this section.'
        raise cherrypy.HTTPRedirect('/index')

