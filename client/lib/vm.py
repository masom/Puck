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

import os, sys, json

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
        self.interfaces = NetInterfaces.getInterfaces()
        self.configured = False

        self._persist_file = '/usr/local/etc/puck_vm'
        self._load()

    def update(self, **kwargs):
        valid = ['keys', 'environment']
        for key in kwargs:
            if not key in valid:
                continue
            setattr(self, key, kwargs[key])

        if 'jails' in kwargs:
            self._set_jails(kwargs['jails'])

        self.configurationValid()

    def _set_jails(self, jails):
        for data in jails:
            if self.jails.contain(data['id']):
                continue
            jail = self.jails.create(data)
            self.jails.add(jail)

    def _load(self):
        if not os.path.exists(self._persist_file):
            return

        keys = ['id', 'jails', 'keys', 'status', 'environment', 'configured']
        data = {}
        with open(self._persist_file, 'r') as f:
            data = json.load(f)

        for key in keys:
            if not key in data:
                #discard loaded data.
                raise KeyError("Key: %s is missing" % key)

        for key in keys:
            setattr(self, key, data[key])

    def persist(self):
        data = {}
        data['id'] = self.id
        data['jails'] = self.jails
        data['keys'] = self.keys
        data['status'] = self.status
        data['environment'] = self.environment
        data['configured'] = self.configured

        with open(self._persist_file, 'w') as f:
            f.write(json.dumps(data, sort_keys=True, indent=4))

    def configurationValid(self):
        listItems = [self.jails.get(), self.keys]
        boolItems = [self.environment]

        for item in listItems:
            if len(item) == 0:
                return self.isConfigured(False)

        for item in boolItems:
            if not item:
                return self.isConfigured(False)

        return self.isConfigured(True)

    def isConfigured(self, state = None):
        if state:
            self.configured = state
            self.status = 'configured'
        elif state == False:
            self.status = 'new'

        return self.configured