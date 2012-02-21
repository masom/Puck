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
from pixie.lib.vm import VM

class MockTransport(object):
    '''
    This mimic a requester. Used by unit tests.
    '''
    def __init__(self):
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
            'environments': self._getEnvironments,
            'yum_repos': self._getYumRepo,
        }.get(resource, None)
        if not method:
            raise NotImplementedError()
        return method()

    def _getRegistration(self):
        registration =  {
            'id': 'ABC-DEF', 'status': 'new', 'name': 'troll',
            'ip': '10.0.0.1', 'instance_type_id': '1', 'instance_id': '1',
            'image_id': '2', 'user': 'msamson', 'config': ''
        }
        return registration

    def _getJails(self):
        jails = {'content': {}, 'database': {}, 'support': {}}

        jails['content']['1'] = {'id': '1', 'type': 'content', 'url': 'http://localhost', 'name': 'Content', 'ip': '10.0.0.10', 'netmask': '255.255.255.0'}
        jails['content']['4'] = {'id': '4', 'type': 'content', 'url': 'http://localhost', 'name': 'Content w/ xdebug', 'ip': '10.0.0.10', 'netmask': '255.255.255.0'}

        jails['database']['2'] = {'id':'2', 'type': 'database', 'url': 'http://localhost', 'name': 'Database', 'ip': '10.0.0.11', 'netmask': '255.255.255.0'}
        jails['database']['5'] = {'id':'5', 'type': 'database', 'url': 'http://localhost', 'name': 'Database w/ new PMS', 'ip': '10.0.0.11', 'netmask': '255.255.255.0'}
        jails['support']['3'] = {'id': '3', 'type': 'support', 'url': 'http://localhost', 'name': 'Support', 'ip': '10.0.0.12', 'netmask': '255.255.255.0'}
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
        environments = [
            {'id': 'foo', 'code': 'dev', 'name': 'Development'},
            {'id': 'bar', 'code': 'prod', 'name': 'Production'}
        ]
        return environments

    def _getYumRepo(self):
        repo = {'data': '''[fedora]
            name=Fedora $releasever - $basearch
            failovermethod=priority
            #baseurl=http://download.fedoraproject.org/pub/fedora/linux/releases/$releasever/Everything/$basearch/os/
            mirrorlist=https://mirrors.fedoraproject.org/metalink?repo=fedora-$releasever&arch=$basearch
            enabled=1
            metadata_expire=7d
            gpgcheck=1
            gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-$basearch'''
        }
        return repo

class JSONTransport(object):
    '''
    Handles commmunication with Puck using JSON for data encoding.
    '''
    def __init__(self):
        self._base = cherrypy.config.get('puck.api_url')

        opener = urllib2.build_opener(urllib2.HTTPHandler)
        self._open = opener.open


    def post(self, resource, id=None, data=''):
        if id:
            resource += '/%s' % id
        return self._request('POST', resource, data=data)

    def get(self, resource, id=None, **params):
        if id:
            resource += '/%s' % id
        if params:
            resource += '?' + urllib.urlencode(params)
        return self._request('GET', resource)

    def put(self, resource, id, data=''):
        resource += '/%s' % id
        return self._request('PUT', resource, data=data)

    def _resource(self, *args):
        return '/'.join((self._base,) + args)

    def _request(self, method, resource, data=None):
        try:
            if data:
                data = json.dumps(data)
        except ValueError:
            data = None

        request = urllib2.Request(self._resource(resource), data=data)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda : method

        try:
            data = json.load(self._open(request))
        except urllib2.HTTPError as e:
            # @TODO: Logging
            return None
        except ValueError as e:
            return None
        return data

class Puck(object):
    '''
    Puck API Client
    '''
    def __init__(self, vm=VM, transport=None):
        self._registration = None

        self._registration_file = cherrypy.config.get('puck.registration_file')

        if not transport:
            transport = cherrypy.config.get('puck.transport')

        self._client = transport()

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
        exists = os.path.exists(self._registration_file)
        if not exists or not self._loadRegistration():
            self._registration = self._client.post('registration')
        return self._saveRegistration()

    def _loadRegistration(self):
        '''
        Load the registration from persistent storage
        @raise IOError when the file could not be read.
        '''

        if not os.path.exists(self._registration_file):
            return False

        with open(self._registration_file, 'r') as f:
            id = f.readline().strip()
            self._registration = self._client.get('registration', id)
        return self._registration

    def _saveRegistration(self):
        '''
        Save the registration code to persistent storagea
        @raise IOError when the file could not be written
        '''
        with open(self._registration_file, 'w') as f:
            f.write(self._registration['id'])
        return True

    def getJails(self, env):
        '''
        Get the jail list assigned to the designated environment.
        '''
        return self._client.get('jails', environment=env)

    def updateStatus(self):
        '''
        Tell Puck about VM status changes
        '''
        data = {
                'id': self.vm.id,
                'status': self.vm.status
        }
        self._client.put('status', self.vm.id, data)

    def updateConfig(self):
        '''
        Send to PUCK the VM configuration.
        '''
        data = {
            'id': self.vm.id,
            'config': self._vm.getConfiguration()
        }
        self._client.put('config', self.vm.id, data)

    def getKeys(self):
        '''
        Get a list of public ssh keys from Puck.
        '''
        return self._client.get("keys")

    def getEnvironments(self):
        '''
        Get the environment list.
        '''
        return self._client.get('environments')

    def getYumRepo(self, env):
        '''
        Get the YUM repository configuration file.
        '''
        return self._client.get('yum_repos', environment=env)
