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

class Credentials(object):
    ''' User credentials abstraction object. '''

    def __init__(self, cloud_url=None, access_key=None, secret_key=None, region=None, name=None, email=None):
        self.cloud_url = cloud_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.name = name
        self.email = email
