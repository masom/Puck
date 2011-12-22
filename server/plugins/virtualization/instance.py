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
    def __init__(self, id = None, backend = None, launch_time = None, ip = None, state = None):
        
        '''Generic attributes'''
        self.id = id
        self.backend = backend
        self.launch_time = launch_time
        self.ip = ip
        self.state = state