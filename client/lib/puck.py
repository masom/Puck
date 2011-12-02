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

class MockRequester(object):
    '''
    This mimick a requester. Used by unit tests.
    '''
    def __init__(self, base):
        pass

    def post(self, resource, data=''):
        return self._switch(resource)

    def get(self, resource, **params):
        return self._switch(resource)

    def put(self, resource, data=''):
        return self._switch(resource)

    def _switch(self, resource):
        method = {
            'registration': self._getRegistration,
            'jails': self._getJails,
            'keys': self._getKeys,
            'environments': self._getEnvironments
        }.get(resource, None)
        if not method:
            raise NotImplementedError()
        return method()

    def _getRegistration(self):
        return {'id': 'ABC-DEF'}

    def _getJails(self):
        jails = {'content': {}, 'database': {}, 'support': {}}

        jails['content']['1'] = {'id': '1', 'type': 'content', 'url': 'http://localhost', 'name': 'Content', 'ip': '10.0.0.10'}
        jails['content']['4'] = {'id': '4', 'type': 'content', 'url': 'http://localhost', 'name': 'Content w/ xdebug', 'ip': '10.0.0.10'}

        jails['database']['2'] = {'id':'2', 'type': 'database', 'url': 'http://localhost', 'name': 'Database', 'ip': '10.0.0.11'}
        jails['database']['5'] = {'id':'5', 'type': 'database', 'url': 'http://localhost', 'name': 'Database w/ new PMS', 'ip': '10.0.0.11'}
        jails['support']['3'] = {'id': '3', 'type': 'support', 'url': 'http://localhost', 'name': 'Support', 'ip': '10.0.0.12'}
        return jails

    def _getKeys(self):
        keys = {
            'derp': {
                'id': 'derp',
                'name': 'Martin Samson',
                'key': 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEArsIuqG9Wictam3s6cwQdW0eedJYuoMbvF7kJ9oFprfo1UEsep30G67SPSUNwuIOIqvUwErFkiNAGjTqdnL8g7PHUInLojM3KQSGSvPgYYAZz9u9wYTy5vv2f/EphBx+FytISjoW1gL8CoiP/kX0vDLpDJnFeRQ/RbvRbiws49r/yqqf/KqXM/fwl1nhQeqwNS6K8kv3H8aaaq7cHqky0xbiDf7astFQq++jRjLIx6xX0NdU8P36IwdMFoQXdnh1B8OvMuyCxHj9y5B2wN2H/1kA0tk0dEQa1BtKNqpJF8HD2AbcTGzYczcvaCMbMV1qJe5/YTQMxjullp2cz/83Hjw=='
            },
            'derpy': {
                'id': 'derpy',
                'name': 'Derpy Samson',
                'key': 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEArsIuqG9Wictam3sDERPedJYuoMbvF7kJ9oFprfo1UEsep30G67SPSUNwuIOIqvUwErFkiNAGjTqdnL8g7PHUInLojM3KQSGSvPgYYAZz9u9wYTy5vv2f/EphBx+FytISjoW1gL8CoiP/kX0vDLpDJnFeRQ/RbvRbiws49r/yqqf/KqXM/fwl1nhQeqwNS6K8kv3H8aaaq7cHqky0xbiDf7astFQq++jRjLIx6xX0NdU8P36IwdMFoQXdnh1B8OvMuyCxHj9y5B2wN2H/1kA0tk0dEQa1BtKNqpJF8HD2AbcTGzYczcvaCMbMV1qJe5/YTQMxjullp2cz/83Hjw=='
            }
        }
        return keys

    def _getEnvironments(self):
        environments = {
            'dev': 'Development',
            'testing': 'Testing',
            'qa': 'Quality Assurance',
            'staging': 'Staging',
            'prod': 'Production'
        }
        return environments

class JSONRequester(object):
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
    def __init__(self, vm=VM, transport=JSONRequester):
        self._registration = None

        self._registration_file = cherrypy.config.get('puck.registration_file')
        self._puck = transport(cherrypy.config.get('puck.api_url'))

        if not self.register():
            raise LookupError()

        self._vm = vm(self._registration)

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
        self._puck.put('status', data=self.vm.status)

    def updateConfig(self):
        '''
        Send to PUCK the VM configuration.
        '''
        self._puck.put('config', data=self._vm.getConfiguration())

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
