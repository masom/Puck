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
import sys, os

class Jails(object):
    '''
    List of jails in the system
    '''
    def __init__(self):
        self._jails = {}
        self._manager = EzJail()
        self._jail = Jail

    def create(self, config):
        return self._jail(self._manager, config)

    def add(self, jail):
        if jail.id in self._jails:
            raise KeyError()
        self._jails[jail.id] = jail

    def remove(self, jail):
        if not jail.id in self._jails:
            raise KeyError()

        #@todo: Stop the jail / delete it
        del(self._jails[jail.id])

    def get(self, id=None):
        if not id:
            return self._jails.values()

        if not id in self._jails:
            raise KeyError()

        return self._jails[id]

class Jail(object):
    def __init__(self, manager, config):
        self.id = config['id']
        self.url = config['url']
        self.type = config['type']
        self.name = config['name']
        self.ip = config['ip']
        self._manager = manager

    def start(self):
        return self._manager.start(self)
    def stop(self):
        return self._manager.stop(self)
    def status(self):
        return self._manager.status(self)
    def create(self):
        return self._manager.create(self)
    def delete(self):
        return self._manager.delete(self)

class EzJail(object):
    def __init__(self):
        pass
    def start(self, jail):
        pass
    def stop(self, jail):
        pass
    def status(self, jail):
        pass
    def create(self, jail):
        pass
    def delete(self, jail):
        pass