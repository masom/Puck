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
class Instance(object):
    '''Generic instance object used by all backends to translate information upstream.'''

    def __init__(self, item=None, **kwargs):

        '''Generic attributes'''
        attrs =  ['id', 'backend', 'name', 'addresses', 'status']
        [setattr(self, k, None) for k in attrs]
        if item:
            [setattr(self, k, getattr(item, k)) for k in attrs if hasattr(item, k)]
        elif kwargs:
            [setattr(self, k, kwargs[k]) for k in kwargs if k in attrs]

class InstanceType(object):
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
