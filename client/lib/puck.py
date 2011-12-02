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
import os, urllib2, urllib, json 
import cherrypy
from vm import VM

class JSONRequest(object):
    '''
    Handles commmunication with Puck using JSON for data encoding.
    '''
    def __init__(self, base):
        self._base = base

        opener = urllib2.build_opener(urllib2.HTTPHandler)
        self._open = opener.open


    def post(self, resource, data=''):
        return self._request('POST', resource, data=data)

    def get(self, resource, **params):
	if params:
		resource += '?' + urllib.urlencode(params)
        return json.load(self._request('GET', resource))

    def put(self, resource, data=''):
        return self._request('PUT', resource, data=data)

    def _resource(self, *args):
        return '/'.join((self._base,) + args)

    def _request(self, method, resource, data=None):
        request = urllib2.Request(self._resource(resource), data=data)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda : method
        return self._open(request)

class Puck(object):
    '''
    Puck API Client
    '''
    def __init__(self):
        self._registration = None

        self._registration_file = cherrypy.config.get('puck.registration_file')
        self._puck = JSONRequest(cherrypy.config.get('puck.api_url'))

        if not self.register():
            raise LookupError()

        self._vm = VM(self._registration)

    def getVM(self):
        '''
        Returns the VM instance the API is attached to.
        '''
        return self._vm

    def register(self):
        '''
        Register the VM to puck.
        Essentially it lets puck know the VM exists.
        '''
        if not os.path.exists(self._registration_file):
            self._getRegistration()
            return self._saveRegistration()

        if not self._loadRegistration():
            self._getRegistration()

        return self._saveRegistration()

    def _getRegistration(self):
        '''
        Post the VM to puck and receive back the registration details.
        '''
        info = self._puck.post('registration')
        self._registration = info['id']

    def _loadRegistration(self):
        '''
        Load the registration from persistent storage
        '''
        with open(self._registration_file, 'r') as f:
            self._registration = f.readline().strip()
        return (len(self._registration))

    def _saveRegistration(self):
        '''
        Save the registration code to persistent storage
        '''
        with open(self._registration_file, 'w') as f:
            f.write(self._registration)
        return True

    def getJails(self, env):
        '''
        Get the jail list assigned to the designated environment.
        '''
        return self._puck.get('jails', environment=env)

    def updateStatus(self):
        '''
        Tell Puck about VM status changes
        '''
        pass

    def updateConfig(self):
        '''
        Send to PUCK the VM configuration.
        '''
        pass

    def getKeys(self):
        '''
        Get a list of public ssh keys from Puck.
        '''
        return self._puck.get("keys")

    def getEnvironments(self):
        '''
        Get the environment list.
        '''
        return self._puck.get('environments')
