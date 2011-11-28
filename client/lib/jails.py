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
import sys, os, shlex, subprocess

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
        data = stdoutdata.splitlines(True)
        if not jail:
            return data

        for line in data:
            found = line.find(jail)
            if found < 0:
                #Line is not about this jail
                continue

            #TODO: Parse line
            return line
        
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
        raise NotImplementedError()
