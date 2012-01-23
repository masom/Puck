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
from interfaces import NetInterfaces
from jails import Jails

import os, sys, json, cherrypy

class VM(object):
    '''
    Virtual Machine
    '''

    def __init__(self, id = None):
        self.id = id
        self.jails = Jails()
        self.keys = {}
        self.status = 'new'
        self.environment = None
        self.interface = None

        self.interfaces = NetInterfaces.getInterfaces()
        self.configured = False

        self._persist_file = cherrypy.config.get('vm.persistence')
        self._load()

    def update(self, **kwargs):
        '''Update the VM object with provided values.'''

        valid = ['keys', 'interface']

        for key in kwargs:
            if not key in valid:
                continue
            setattr(self, key, kwargs[key])

        if 'environment' in kwargs:
            old_env = self.environment
            self.environment = kwargs['environment']

            if old_env != self.environment:
                self.jails.clear()

        if 'jails' in kwargs:
            self._set_jails(kwargs['jails'])

        self.configurationValid()

    def _set_jails(self, jails):
        '''Sets the jails to the provided list.'''

        self.jails.clear()

        for data in jails:
            if self.jails.contain(data['id']):
                continue
            jail = self.jails.create(data)
            self.jails.add(jail)

    def _load(self):
        '''Load the vm off the persistent storage.'''

        if not os.path.exists(self._persist_file):
            return

        keys = ['id', 'keys', 'status', 'environment', 'configured', 'interface']
        data = {}

        try:
            with open(self._persist_file, 'r') as f:
                data = json.load(f)
        except ValueError as e:
            return

        for key in keys:
            if not key in data:
                #discard loaded data.
                raise KeyError("Key: `%s` is missing." % key)

        if not 'jails' in data:
            raise KeyError("Key: `jails` is missing.")

        for key in keys:
            setattr(self, key, data[key])

        self.jails.load(data['jails'])

    def persist(self):
        '''Saves the VM to the persistent storage.'''

        data = self.getConfiguration()
        with open(self._persist_file, 'w') as f:
            f.write(json.dumps(data, sort_keys=True, indent=4))

    def getConfiguration(self):
        '''Returns a dictionary filled with the VM configuration data.'''

        data = {}
        data['id'] = self.id
        data['jails'] = self.jails.export()
        data['keys'] = self.keys
        data['status'] = self.status
        data['environment'] = self.environment
        data['configured'] = self.configured
        data['interface'] = self.interface
        return data

    def configurationValid(self):
        '''Verifies if the configuration is valid and upate the jail status accordingly'''

        listItems = [self.jails.get(), self.keys]
        boolItems = [self.environment, self.interface]

        for item in listItems:
            if len(item) == 0:
                return self.isConfigured(False)

        for item in boolItems:
            if not item:
                return self.isConfigured(False)

        return self.isConfigured(True)

    def isConfigured(self, state = None):
        '''Switch the configuration state or returns it.'''

        if state:
            self.configured = state
            self.status = 'configured'
        elif state == False:
            self.configured = state
            self.status = 'new'

        return self.configured
