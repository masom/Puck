'''
Pixie: FreeBSD virtualization guest configuration client
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

class Controller(object):
    '''
    Base controller class.
    Defines functions used by all controllers.
    '''

    def __init__(self, lookup):
        self.lookup = lookup

    def _cp_on_error(self):
        cherrypy.response.body = ("We apologise for the fault in the website. "
                                  "Those responsible have been sacked.")

    def render(self, template, **variables):
        variables['flash'] = cherrypy.session.pop('flash', None)
        tmpl = self.lookup.get_template(template)
        return tmpl.render(**variables)
