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
        '''Returns the number of jails'''
        return len(self._jails)

    def setSocket(self, ezjl_socket):
        '''Sets the create socket to the jail manager. Ugly hack.'''
        self._manager.setSocket(ezjl_socket)

    def load(self, jails):
        '''
        Load jails from a saved vm.
        '''
        for j in jails:
            self.add(self.create(j))

    def create(self, config):
        '''Creates a new jail, returning it'''
        return self._jail(self._manager, config)

    def add(self, jail):
        '''Add a jail
        raises KeyError if the jail already exists.'''
        if jail.id in self._jails:
            raise KeyError()
        self._jails[jail.id] = jail

    def remove(self, jail):
        '''Remove a jail.
        raises KeyError if the jail does not exists.'''
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
        '''Clear the jail registry'''
        self._jails.clear()

    def export(self):
        '''Exports the jail as a list'''
        jails = []
        for j in self._jails:
            jails.append(self._jails[j].export())
        return jails

    def get(self, id=None):
        '''Gets a jail
        raises KeyError if the jail was not found.'''
        if not id:
            return self._jails.values()

        if not id in self._jails:
            raise KeyError()

        return self._jails[id]

    def status(self):
        '''Returns the status of the jails.'''
        return self._manager.status()

class Jail(object):
    def __init__(self, manager, config):
        self._data = {}

        keys = ['id', 'url', 'type', 'name', 'ip', 'netmask']
        for k in keys:
            if not k in config:
                raise KeyError("Configuration value `%s` is not set." % k)
            self._data[k] = config[k]

        self._manager = manager

    def export(self):
        '''Export the jail data.'''
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
        '''Starts the jail'''
        return self._manager.start(self._data['type'])

    def stop(self):
        '''Stops the jail'''
        return self._manager.stop(self._data['type'])

    def status(self):
        '''Get the jail status'''
        return self._manager.status(self._data['type'])

    def create(self):
        '''Create a jail
        Here we make the assumption the type is the same as the flavour...
        Will need to refactor for more global use than HCN's
        '''
        return self._manager.create(self._data['type'], self._data['type'], self._data['ip'])

    def delete(self):
        return self._manager.delete(self._data['type'])

class EzJail(object):

    def __init__(self):
        self.logs = []
        self._prog = '/usr/local/bin/ezjail-admin'

    def setSocket(self, ezjl_socket):
        '''Set the socket used to communicate with the fork handling jail start.'''
        self._socket = ezjl_socket

    def install(self):
        '''
        Installs ezjail
        @raise OSError when command not found.
        '''
        command = '%s install -m -p' % self._prog
        self.logs.append(command)

        subprocess.Popen(shlex.split(command)).wait()

    def start(self, jail = None):
        '''
        Starts the jails or a specific jail
        @raise OSError when command not found.
        '''
        self._socket.send(json.dumps({'id': 'start', 'name': jail}))
        '''block while we wait for completion'''
        status = self._socket.recv(512)
        print status
        # @TODO handle status

    def stop(self, jail = None):
        '''
        Stops the jails or a specific jail
        @raise OSError when command not found.
        '''

        command = "%s stop" % self._prog
        if jail:
            command += " %s" % str(jail)
        self.logs.append(command)
        subprocess.Popen(shlex.split(command)).wait()

    def status(self, jail = None):
        '''
        Gives the status the installed jails.
        @raise OSError when command not found.
        @raise KeyError when jail not found.
        @return list
        '''

        command = "%s list" % self._prog
        output = subprocess.check_output(shlex.split(command))

        if len(output) == 0:
            raise RuntimeError("No data returned by ezjail.")

        data = output.splitlines(False)
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

        # ezjail-admin create -f [flavour] [name] [ip]

        # shlex does not support unicode with python < 2.7.3
        cmd = str("%s create -f %s %s %s" % (self._prog, flavour, name, ip))
        self.logs.append(cmd)

        subprocess.Popen(shlex.split(cmd)).wait()

    def delete(self, jail):
        '''
        Deletes a jail from the system
        '''

        commands = [
            "%s stop %s" % (self._prog, jail),
            "%s delete -w %s" % (self._prog, jail)
        ]
        for command in commands:
            self.logs.append(command)

            subprocess.Popen(shlex.split(str(command))).wait()

class StopLoopException(Exception): pass
class EzJailStarter(object):
    '''Workaround for python thread breaking jail start.'''

    def getSocketFile(self):
        '''Generate a file to be used as UNIX socket'''

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
            try:
                data = conn.recv(4096)
            except:
                break

            print "Received data: `%s`" % data

            (execute, command) = self._handle(data)

            if execute:
                try:
                    execute(command)
                except StopLoopException:
                    break
            conn.send(json.dumps({"status": "started"}))
        conn.close()

    def _handle(self, data):
        '''
        Handles incoming requests
        '''
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

        return (execute, command)

    def _startJail(self, data):
        '''
        Starts a jail
        '''
        cmd = "ezjail-admin start %s" % str(data['name'])
        conn.send(json.dumps({"status": "starting", "command": cmd}))
        subprocess.Popen(shlex.split(cmd)).wait()

    def _stop(self, data):
        '''
        Request the jailstarter to be stopped.
        '''
        raise StopLoopException()
