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
import pickle
import cherrypy

class Credentials(object):
    ''' User credentials abstraction object. '''

    def __init__(self, name=None, email=None, password=None, data=None):
        self.name = name
        self.email = email
        self.password = password
        self._data = {}

        # Auth data is stored as a pickled object in a text field.
        if data:
            self._load_data(data)
        self._post_init()

    def _load_data(self, data):
        try:
            self._data = pickle.loads(data)
        except pickle.PickleError as e:
            #TODO log
            pass

    def _post_init(self):
        '''Intended to be overloaded.'''
        pass

