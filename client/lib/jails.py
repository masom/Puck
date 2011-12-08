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

'''For the EzjailCreator workaround'''
import socket, json

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

    def setSocket(self, ezjl_socket):
        self._manager.setSocket(ezjl_socket)

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
        '''
        Here we make the assumption the type is the same as the flavour...
        Will need to refactor for more global use than HCN's
        '''
        return self._manager.create(self._data['type'], self._data['type'], self._data['ip'])

    def delete(self):
        return self._manager.delete(self._data['type'])

class EzJail(object):

    def setSocket(self, ezjl_socket):
        self._socket = ezjl_socket

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
        self._socket.send(json.dumps({'id': 'start', 'name': jail}))
        '''block while we wait for completion'''
        status = self._socket.recv(512)
        print status

    def stop(self, jail = None):
        '''
        Stops the jails or a specific jail
        @raise OSError when command not found.
        '''

        command = "ezjail-admin stop"
        if jail:
            command += " %s" % str(jail)

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

        if len(stdoutdata) == 0:
            raise RuntimeError("No data returned by ezjail.")

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
        '''TODO logging? '''

    def delete(self, jail):
        '''
        Deletes a jail from the system
        '''

        commands = [
            "ezjail-admin stop %s" % jail,
            "ezjail-admin delete -w %s" % jail
        ]
        for command in commands:
            (stdoutdata, stderrdata) = subprocess.Popen(shlex.split(str(command))).communicate()
            print
            print
            print stdoutdata
            print stderrdata
            print
            print

class StopLoopException(Exception): pass
class EzJailStarter(object):
    '''Workaround for python thread breaking jail start.'''


    def getSocketFile(self):
        '''Initialize the communication socket'''

        self._socket_file = "/tmp/pixie_ezc_%s" % os.getpid()
        return self._socket_file

    def teardown(self):
        self._socket.close()

    def run(self):
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._socket.bind(self._socket_file)
        self._socket.listen(1)

        (conn, addr) = self._socket.accept()
        while True:
            data = conn.recv(4096)

            print "Received data: `%s`" % data

            (execute, data) = self._handle(data)

            if execute:
                try:
                    execute(data)
                except StopIteration:
                    break
            conn.send("started")
        conn.close()

    def _handle(self, data):
        try:
            command  = json.loads(data)
        except ValueError:
            return (False, False)

        if not 'id' in command:
            return (False, False)

        execute = {
            'shutdown': self._stop,
            'start': self._startJail
        }.get(command['id'], False)

        return (execute, data)

    def _startJail(self, data):
        cmd = "ezjail-admin start %s" % str(data['name'])
        subprocess.Popen(shlex.split(cmd)).wait()

    def _stop(self, data):
        raise StopLoopException()