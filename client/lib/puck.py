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
import os
from vm import VM

class Puck(object):
    '''
    Puck API Client
    '''
    def __init__(self):
        self._registration = None

        #TODO: Move this to a cherrypy configuration value
        self._registration_file = '/usr/local/etc/puck_registration'
        if not self.register():
            raise LookupError()

        self._vm = VM(self._registration)


    def getVM(self):
        return self._vm

    def register(self):
        '''
        TODO: USE API
        '''
        if not os.path.exists(self._registration_file):
            self._getRegistration()
            return self._saveRegistration()

        if not self._loadRegistration():
            self._getRegistration()

        return self._saveRegistration()

    def _getRegistration(self):
        '''
        Get the registration code
        @todo: Use API
        '''
        self._registration = 'ABC-DEF'

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

    def getJails(self):
        '''
        @todo: USE API
        '''
        jails = {'content': {}, 'database': {}, 'support': {}}

        jails['content']['1'] = {'id': '1', 'type': 'content', 'url': 'http://localhost', 'name': 'Content', 'ip': '10.0.0.10'}
        jails['content']['4'] = {'id': '4', 'type': 'content', 'url': 'http://localhost', 'name': 'Content w/ xdebug', 'ip': '10.0.0.10'}

        jails['database']['2'] = {'id':'2', 'type': 'database', 'url': 'http://localhost', 'name': 'Database', 'ip': '10.0.0.11'}
        jails['database']['5'] = {'id':'5', 'type': 'database', 'url': 'http://localhost', 'name': 'Database w/ new PMS', 'ip': '10.0.0.11'}
        jails['support']['3'] = {'id': '3', 'type': 'support', 'url': 'http://localhost', 'name': 'Support', 'ip': '10.0.0.12'}
        return jails

    def updateStatus(self):
        pass

    def updateConfig(self):
        pass

    def getKeys(self):
        '''
        TODO: Use API
        '''
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

    def getEnvironments(self):
        '''
        TODO: Use API
        '''
        environments = {
            'dev': 'Development',
            'testing': 'Testing',
            'qa': 'Quality Assurance',
            'staging': 'Staging',
            'prod': 'Production'
        }
        return environments