'''
Pixie: FreeBSD virtualization guest configuration client
Copyright (C) 2011  The Hotel Communication Network inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.f

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import sys, os, shlex, subprocess

class Jails(object):
    '''
    List of jails in the system
    '''
    def __init__(self):
        self._jails = {}
        self._manager = EzJail()
        self._jail = Jail

    def __iter__(self):
        for i in self._jails:
            yield self._jails[i]

    def count(self):
        return len(self._jails)

    def load(self, jails):
        '''
        Load jails from a saved vm.
        '''
        for j in jails:
            self.add(self.create(j))

    def create(self, config):
        return self._jail(self._manager, config)

    def add(self, jail):
        if jail.id in self._jails:
            raise KeyError()
        self._jails[jail.id] = jail

    def remove(self, jail):
        if not jail.id in self._jails:
            raise KeyError()

        try:
            self._jails[jail.id].stop()
            self._jails[jail.id].delete()
        except KeyError as e:
            pass
        del(self._jails[jail.id])

    def contain(self, id):
        return id in self._jails

    def clear(self):
        self._jails.clear()

    def export(self):
        jails = []
        for j in self._jails:
            jails.append(self._jails[j].export())
        return jails
 
    def get(self, id=None):
        if not id:
            return self._jails.values()

        if not id in self._jails:
            raise KeyError()

        return self._jails[id]

class Jail(object):
    def __init__(self, manager, config):
        self._data = {}

        keys = ['id', 'url', 'type', 'name', 'ip']
        for k in keys:
            if not k in config:
                raise KeyError("Configuration value `%s` is not set." % k)
            self._data[k] = config[k]

        self._manager = manager

    def export(self):
        return self._data

    def __getattr__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return object.__getattribute__(self, "_data")[name]

    def __setattr__(self, name, value):
        if hasattr(self, name) or name in ['_data','_manager']:
            return object.__setattr__(self, name, value)
        object.__getattribute__(self, "_data")[name] = value
        return

    def start(self):
        return self._manager.start(self._data['type'])
    def stop(self):
        return self._manager.stop(self._data['type'])
    def status(self):
        return self._manager.status(self._data['type'])
    def create(self):
        return self._manager.create(self, self._data['flavour'], self._data['type'], self._data['ip'])
    def delete(self):
        return self._manager.delete(self._data['type'])

class EzJail(object):

    def install(self):
        '''
        Installs ezjail
        @raise OSError when command not found.
        '''
        command = 'ezjail-admin install -m -p'
        (stdoutdata, stderrdata) = subprocess.Popen(shlex.split(command)).communicate()
        print
        print
        print stdoutdata
        print "---------"
        print stderrdata
        print
        print
        
    def start(self, jail = None):
        '''
        Starts the jails or a specific jail
        @raise OSError when command not found.
        '''

        command = "ezjail-admin start"
        if jail:
            command += " %s" % jail

        (stdoutdata, stderrdata) = subprocess.Popen(shlex.split(command)).communicate()

    def stop(self, jail = None):
        '''
        Stops the jails or a specific jail
        @raise OSError when command not found.
        '''

        command = "ezjail-admin stop"
        if jail:
            command += " %s" % jail

        (stdoutdata, stderrdata) = subprocess.Popen(shlex.split(command)).communicate()

    def status(self, jail = None):
        '''
        Gives the status the installed jails.
        @raise OSError when command not found.
        @raise KeyError when jail not found.
        @return list
        '''

        command = "ezjail-admin list"
        (stdoutdata, stderrdata) = subprocess.Popen(shlex.split(command)).communicate()
        data = stdoutdata.split().splitlines(True)
        if not jail:
            return data

        for line in data[2:]:
            found = line.find(jail)
            if found < 0:
                continue
            return data[:2] + [line]
        raise KeyError("Jail not found.")
        
    def create(self, flavour, name, ip):
        '''
        Creates a new jail based off a flavour, name and ip
        @raise OSError when command not found.
        '''

        '''
        ezjail-admin create -f [flavour] [name] [ip]
        '''
        cmd = "ezjail-admin create -f %s %s %s" % (flavour, name, ip)
        (stdoutdata, stderrdata) = subprocess.Popen(shlex.split(cmd)).communicate()

    def delete(self, jail):
        '''
        Deletes a jail from the system
        '''

        commands = [
            "ezjail-admin stop %s" % jail,
            "ezjail-admin delete -w %s" % jail
        ]
        for command in commands:
            (stdoutdata, stderrdata) = subprocess.Popen(shlex.split(command)).communicate()
